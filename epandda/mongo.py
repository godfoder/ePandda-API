from base import baseResource
import json
from bson import Binary, Code, json_util, BSON, ObjectId
from bson.json_util import dumps

class mongoBasedResource(baseResource):
    def __init__(self):
        super(mongoBasedResource, self).__init__()
