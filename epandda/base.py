from flask import request
from flask_restful import Resource, Api
import json
from pymongo import MongoClient
from bson import Binary, Code, json_util, BSON, ObjectId
from bson.json_util import dumps

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


        # Load standard API params
        self.start = self.getRequest().args.get('start') or 0
        self.length = self.getRequest().args.get('length') or 10

    def getRequest(self):
        return request

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
                resolved.append({"occurrence_no": mitem['occurrence_no']})
            resolved_references["pbdb_resolved"] = resolved

        return resolved_references