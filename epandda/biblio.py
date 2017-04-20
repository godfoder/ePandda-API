from mongo import mongoBasedResource
from response_handler import response_handler

#
#
#
class biblio(mongoBasedResource):
    def get(self):

        # Required
        scientific_name = self.getRequest().args.get('scientific_name')
       
        # Optional
        journal         = self.getRequest().args.get('journal')
        article         = self.getRequest().args.get('article')
        author          = self.getRequest().args.get('author')
        state_prov      = self.getRequest().args.get('state_province')
        county          = self.getRequest().args.get('county')
        locality        = self.getRequest().args.get('locality')

        params = [
          {
            "name": "scientific_name",
            "type": "text", 
            "value": scientific_name,
            "required": True,
            "description": "Taxon to search occurrence records for"
          },
          {
            "name": "journal",
            "type": "text",
            "value": journal,
            "required": False,
            "description": "Then name of academic Journal a bibligraphic description would be found"
          },
          {
            "name": "article",
            "type": "text",
            "value": article,
            "required": False,
            "description": "The name of the journal article the given scientific_name appears in"
          },
          {
            "name": "author",
            "type": "text",
            "value": author,
            "required": False,
            "description": "The name of the author who's article describes the given scientific_name"
          },
          {
            "name": "state_province",
            "type": "text",
            "value": state_prov,
            "required": False,
            "description": "The state/province to search for scientific_name and publication references"
          },
          {
            "name": "county",
            "type": "text",
            "value": county,
            "required": False,
            "descripiton": "The county to search for scientific_name and publication references"
          },
          {
            "name": "locality",
            "type": "text",
            "value": locality,
            "required": False,
            "description": "The locality name to search for scientific_name occurences and publication references"
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
            'endpoint_description': 'returns specimen occurrence and publication records for a given scientific name. results can be filtered by the optional params',
            'params': params
          }
          
        return response_handler( resp )
