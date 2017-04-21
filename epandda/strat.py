from mongo import mongoBasedResource
from response_handler import response_handler
from flask_restful import reqparse

parser = reqparse.RequestParser()

parser.add_argument('scientific_name', type=str, help='taxonomic name to search stratigraphy for')
parser.add_argument('formation', type=str, help='formation name to filter taxonomic results by')
parser.add_argument('state_province', type=str, help='state or province name to filter taxonomic results by')
parser.add_argument('county', type=str, help='county name to filter taxonomic results by')
parser.add_argument('locality', type=str, help='locality name to filter taxonomic results by')

#
#
#
class stratigraphy(mongoBasedResource):
    def get(self):

        # Required
        scientific_name = self.getRequest().args.get('scientific_name')
        formation       = self.getRequest().args.get('formation')

        # Optional
        state_prov      = self.getRequest().args.get('state_province')
        county          = self.getRequest().args.get('county')
        locality        = self.getRequest().args.get('locality')       # param
        

        params = [
          {
            "name": "scientific_name",
            "type": "text",
            "value": scientific_name,
            "required": True,
            "description": "The taxon being searched in a given stratigraphic range"
          },
          {
            "name": "formation",
            "type": "text",
            "value": formation,
            "required": True,
            "description": "The geologic formation to search for provided taxa"
          },
          {
            "name": "state_province",
            "type": "text",
            "value": state_prov,
            "required": False,
            "description": "The state or province to constrain the search of a given taxa in a given formation"
          },
          {
            "name": "county",
            "type": "text",
            "value": county,
            "required": False,
            "description": "The county to constrain the search of a given taxa in a given formation"
          },
          {
            "name": "locality",
            "type": "text",
            "value": locality,
            "required": False,
            "description": "A locality to constrain the search of a given taxa in a given formation"
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

          d = self.resolveReferences(d)
          resp = self.toJson(d)

        else:

          resp = {
            'endpoint_description': 'Returns specicmen occurrence records from a given formation',
            'params': params
          }

        return response_handler( resp )

    def post(self):
      args = parser.parse_args()
 
      resp = {
        'endpoint_description': 'Returns specimen occurrence with stratigraphic records from a given formation',
        'params': args
      }

      return response_handler( resp )
