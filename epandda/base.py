from flask import request, Response
from flask_restful import Resource, Api
import json
from pymongo import MongoClient
from bson import Binary, Code, json_util, BSON, ObjectId
from bson.json_util import dumps
import datetime

#
# Base class for API resource
# Sets up environment shared by all API calls, such as loading the API config file
#

class baseResource(Resource):
    def __init__(self):
        super(baseResource, self).__init__()

        # Load API config
        self.config = json.load(open('./config.json'))

        self.client = MongoClient("mongodb://" + self.config['mongodb_user'] + ":" + self.config['mongodb_password'] + "@" + self.config['mongodb_host'])
        self.idigbio = self.client.idigbio.occurrence
        self.pbdb = self.client.test.pbdb_flat_index

        self.params = {}
        self.paramCount = 0;

    #
    # Return request object
    #
    def getRequest(self):
        return request

    #
    # Resolve underlying data source ids (from iDigBio, PBDB, Etc.) to URLs the end-user can use
    #
    def resolveReferences(self, data):
        resolved_references = {}
        for item in data:
            # resolve idigbio refs
            ids = map(lambda id: ObjectId(id), item["matches"]["idigbio"])
            m = self.idigbio.find({"_id": {"$in" : ids}})

            resolved = []
            for mitem in m:
                resolved.append({"uuid": mitem['idigbio:uuid'], "url": "https://www.idigbio.org/portal/records/" + mitem['idigbio:uuid']})
            resolved_references["idigbio_resolved"] = resolved

            # resolve pbdb refs
            ids = map(lambda id: ObjectId(id), item["matches"]["pbdb"])
            m = self.pbdb.find({"_id": {"$in": ids}})

            resolved = []
            for mitem in m:
                resolved.append('https://paleobiodb.org/data1.2/occs/single.json?id=' + mitem['occurrence_no'] + '&show=full')
            resolved_references["pbdb_resolved"] = resolved

        return resolved_references

    #
    # params = list of param keys
    #
    def getParams(self):
        desc = self.description()['params'][:]
        r = self.getRequest()
        r_as_json = request.get_json(silent=True)

        # always pull offset and limit params
        desc.append({"name": "offset"})
        desc.append({"name": "limit"})

        self.params = {}

        c = 0
        errors = {}
        for p in desc:
            # JSON blob
            if r_as_json is not None:
                if(p['name'] in r_as_json):
                    self.params[p['name']] = r_as_json[p['name']]
                    c = c + 1
                else:
                    self.params[p['name']] = None

            # POST request
            elif request.method == 'POST':
                if(p['name'] in request.form):
                    self.params[p['name']] = request.form[p['name']]
                    c = c + 1
                else:
                    self.params[p['name']] = None

            # GET request
            elif request.method == 'GET':
                v = r.args.get(p['name'])
                if (v):
                    self.params[p['name']] = v
                    c = c + 1
                else:
                    self.params[p['name']] = None

            # Throw errors for missing required values
            if 'required' in p and p['required'] and (self.params[p['name']] is None or len(self.params[p['name']]) == 0):
                errors[p['name']] = "No value for required parameter " + p['name']

        self.paramCount = c

        if len(errors) > 0:
            raise Exception(errors)

        return self.params

    #
    # Get row offset for returned result set
    #
    def offset(self):
        if self.params is None or self.params.get('offset') is None:
            self.getParams()
        return 0 if self.params['offset'] is None else int(self.params['offset'])

    #
    # Get maximum number of records to return in result set
    #
    def limit(self):
        if self.params is None or self.params.get('limit') is None:
            self.getParams()
        return 100 if self.params['limit'] is None else int(self.params['limit'])

    #
    # Default description block for endpoints that don't describe themselves
    #
    def description(self):
        return {
            'maintainer': 'Orphan Pandda',
            'maintainer_email': 'orphan@epandda.org',
            'name': '[NO NAME]',
            'description': '[NO DESCRIPTION]',
            'params': [{
                "name": "sample_parameter",
                "type": "text",
                "required": False,
                "description": "If the endpoint maintainer had bothered to document the available parameters, each parameter would be described in this format."
            }]
        }

    #
    # Return data object as string
    #
    def serialize(self, data):
        return dumps(data)

    #
    # Return data object as JSON. Can handle Mongo cursors.
    #
    def toJson(self, data):
        # Serialize Mongo cursor as JSON
        json_data = json.loads(dumps(data, sort_keys=True, indent=4, default=json_util.default))

        # Kill _id keys (and maybe some others too soon...)
        #for record in json_data:
        #  record.pop('_id', None)
        return json_data


    #
    # Default handler for GET requests
    # (just calls process() and returns response as-is, which should be fine 99.9999999999% of the time)
    #
    def get(self):
        try:
            return self.process()
        except Exception as e:
            return self.respondWithError(e.args[0])

    #
    # Default handler for POST requests
    # (just calls process() and returns response as-is, which should be fine 99.9999999999% of the time)
    #
    def post(self):
        try:
            return self.process()
        except Exception as e:
            return self.respondWithError(e.args[0])

    #
    #
    #
    def getParameterNames(self):
        desc = self.description()

        names = []
        for f in desc['params']:
            names.append(f['name'])

        return names

    #
    # Return an API response. The format of the response can vary based upon
    # respType, of which are supported:
    #
    #   "data" => an API data response for a valid user query [DEFAULT]
    #   "routes" => a list of valid API endpoints, with descriptions for each.
    #
    def respond(self, return_object, respType="data"):
        # Default Response
        if respType == "routes":
            defaults = {
                "description": "",
                "routes": {},
                "timeReturned": str(datetime.datetime.now()),
                "v": self.config['version']
            }
        else:
            defaults = {
                "counts": {},
                "timeReturned": str(datetime.datetime.now()),
                "offset": self.offset(),
                "limit": self.limit(),
                "success": True,
                "specimenData": False,
                "includeAnnotations": False,
                "results": {},
                "criteria": {},
                "v": self.config['version'],
            }

        resp = {}

        for k in defaults:
            if k in return_object:
                resp[k] = return_object[k]
            else:
                resp[k] = defaults[k]

        # Default Mimetype with override handling
        mime_type = "application/json"
        if "mimetype" in return_object:
            mime_type = return_object['mimetype']

        # Default Status Code with override handling
        status_code = 200
        if "status_code" in return_object:
            status_code = return_object['status_code']

        if "data" in return_object:
            resp['data'] = return_object['data']

        if "params" in return_object:
            resp['params'] = return_object['params']

        return Response(response=json.dumps(resp, sort_keys=True, indent=4, separators=(',', ': ')).encode('utf8'),
                        status=status_code, mimetype=mime_type)

    #
    # Respond with description of endpoint. Used when user hits an endpoint with no parameters.
    #
    def respondWithDescription(self):
        return Response(response=json.dumps(self.description(), sort_keys=True, indent=4, separators=(',', ': ')).encode('utf8'),
                        status=200, mimetype="text/json")

    #
    # Respond with error message.
    #
    def respondWithError(self, errors):
        names = self.getParameterNames()

        # process errors, omitting ones not related to a parameter or GENERAL (the generic error heading)
        errors_filtered = {}

        for i in errors:
            if i == "GENERAL" or i in names:
                if type(errors[i]) is list:
                    errors_filtered[i] = errors[i]
                elif type(errors[i]) is tuple:
                    errors_filtered[i] = [v for key in errors[i] for v in key]
                else:
                    errors_filtered[i] = [errors[i]]


        return Response(
            response=json.dumps({"errors": errors_filtered}, sort_keys=True, indent=4, separators=(',', ': ')).encode(
                'utf8'),
            status=500, mimetype="text/json")