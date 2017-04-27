from mongo import mongoBasedResource
from response_handler import response_handler
from flask_restful import reqparse

parser = reqparse.RequestParser()

parser.add_argument('locality', type=str, help='Locality name to to search geoname records by')

#
#
#
class geoname(mongoBasedResource):
    def get(self):
        locality = self.getRequest().args.get('locality')       # param
    	
    	params = [
          {
            "name": "locality",
            "type": "text", 
            "value": locality,
            "required": True,
            "description": "Name of locality to find"
          }
        ]
    
        lindex = self.client.test.spIndex                       # Mongodb index for localities

        if locality:
          res = lindex.find({"$text": {"$search": locality}})

          d = []
          for i in res:
              terms = i['original_terms']
              terms.append(locality)
              item = {"terms": terms, "matches": {"pbdb": i['pbdb_data'], "idigbio": i['idb_data']}}
              d.append(item)

          resp = {'data': self.resolveReferences(d) }
		
        else:

          resp = {
            'endpoint_description': 'Returns specimens collected from a given locality',
            'params': params
          }
          
        return response_handler( resp )

    def post(self):
      args = parser.parse_args()
  
      resp = {
        'endpoint_description': 'Returns geoname records',
        'params': args
      }

      return response_handler( resp )
