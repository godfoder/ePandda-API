from base import baseResource
import json
from bson import Binary, Code, json_util, BSON, ObjectId
from bson.json_util import dumps

class mongoBasedResource(baseResource):
    def __init__(self):
        super(mongoBasedResource, self).__init__()

    def serialize(self, data):
        return dumps(data)

    def toJson(self, data):
        # Serialize Mongo cursor as JSON
        json_data = json.loads(dumps(data, sort_keys=True, indent=4, default=json_util.default))

        # Kill _id keys (and maybe some others too soon...)
        #for record in json_data:
         #  record.pop('_id', None)
        return json_data

    # TODO: move to base.py to allow all resources use of this
