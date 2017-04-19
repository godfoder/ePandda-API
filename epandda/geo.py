from mongo import mongoBasedResource

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

          # TODO: Think how best to automate / make dynamic
          resp = {'success': {
                      'v': 1,
                      'description': 'returns specimens collected from a given locality',
                      'params': {
                         'locality': {
                            'type': 'text',
                            'required': True,
                            'description': 'Name of the Locality where returned specimens were collected.'
                          }
                      }
                    }
                 }

        return resp
