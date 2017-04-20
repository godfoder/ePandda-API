from mongo import mongoBasedResource
from response_handler import response_handler
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
            'endpoint_description': 'returns specicmen occurrence records from a given formation',
            'params': params
          }

        return response_handler( resp )
