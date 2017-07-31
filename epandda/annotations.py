from mongo import mongoBasedResource
from flask_restful import reqparse

parser = reqparse.RequestParser()

#
#
#
class annotations(mongoBasedResource):
    def process(self):

        # Mongodb index for Publication
        annotations = self.client.test.annotations

  
        # returns dictionary of params as defined in endpoint description
        # will throw exception if required param is not present
        params = self.getParams()
        
        # offset and limit returned as ints with default if not set
        offset = self.offset()
        limit = self.limit()

        if limit < 1:
          limit = 100

        annoQuery = []
        if self.paramCount > 0:

          criteria = {
            'endpoint': 'annotation',
            'parameters': {},
            'matchPoints': [],
            'matchTerms': {}
          }

          #for p in ['stateProvinceName', 'author', 'scientific_name', 'journal', 'locality', 'county', 'article']:  

            
          d = []
          idbCount = 0
          pbdbCount = 0

          res = annotations.find({"$and":  annoQuery })

          if res:

            for i in res:
           
              matches['faceted_matches'] = i

              
          finalMatches = {'idigbio': [], 'pbdb': []}
          finalMatches['idigbio'] = matches['idigbio']
          finalMatches['pbdb'] = matches['pbdb']

          idbCount = len(finalMatches['idigbio'])
          pbdbCount = len(finalMatches['pbdb'])
          
          resolveSet = { 'idigbio': finalMatches['idigbio'][offset:limit],
                         'pbdb': finalMatches['pbdb'][offset:limit] }

          d.append({'matches': finalMatches})
          d = self.resolveReferences(d,'refs', 'both' )

          counts = {
            'totalCount': idbCount + pbdbCount, 
            'idbCount': idbCount,
            'pbdbCount': pbdbCount
          }

          return self.respond({
              'counts': counts, 
              'results': d,
              'criteria': criteria,
              'includeAnnotations': params['includeAnnotations'],
              'faceted_matches': matches['faceted_matches']
          })
        else:

          print "Should respond with  Description?"

          return self.respondWithDescription()
            

    def description(self):
        return {
            'name': 'Annotations',
            'maintainer': 'Jon Lauters',
            'maintainer_email': 'jon@epandda.org',
            'description': 'Returns openAnnotations for linked data in ePANDDA.',
            'params': []
        }
                
