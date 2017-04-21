from mongo import mongoBasedResource
from response_handler import response_handler
from flask_restful import reqparse

parser = reqparse.RequestParser()

parser.add_argument('locality', type=str, help='locality name to to search geoname records by')

#
#
#
class geoname(mongoBasedResource):
    def get(self):
        locality = self.getRequest().args.get('locality')       # param
        lindex = self.client.test.spIndex                       # Mongodb index for localities

        if locality:
          res = lindex.find({"$text": {"$search": locality}})

          d = []
          for i in res:
              terms = i['original_terms']
              terms.append(locality)
              item = {"terms": terms, "matches": {"pbdb": i['pbdb_data'], "idigbio": i['idb_data']}}
              d.append(item)

          d = self.resolveReferences(d)
          resp = self.toJson(d)

        else:

          resp = {
            'endpoint_description': 'returns specimens collected from a given locality',
            'params': params
          }
          


        return response_handler( resp )

    def post(self):
      args = parser.parse_args()
  
      resp = {
        'endpoint_description': 'returns geoname records',
        'params': args
      }

      return response_handler( resp )
