import re
from mongo import mongoBasedResource

#
#
#
class annotations(mongoBasedResource):
    def process(self):

        # Mongodb index for Publication
        annotations = self.client.endpoints.annotations
  
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
            'endpoint': 'annotations',
            'parameters': {},
          }

          for p in ['annotationDate']:  
 
            if params[p]:

              if 'annotationDate' == p:
                annoQuery.append({"annotatedAt": { '$regex': params[p]} }) 
            
              criteria['parameters'][p] = str(params[p]).lower()

          d = []
 
          # Total Count:
          annoCount = annotations.find({}).count()

          # Allows for optional Date param since you can't $and on nothing.
          res = annotations.find({}, {'_id': False}).limit(limit).skip(offset)
          if annoQuery:
            res = annotations.find({"$and":  annoQuery }, {'_id': False}).limit(limit).skip(offset)

          if res:
              for i in res:
                  d.append(i)


          counts = {'totalCount': annoCount, 'annotationsCount': len(d)}

          return self.respond({
              'counts': counts, 
              'results': d[offset:limit],
              'criteria': criteria,
          })
        else:

          return self.respondWithDescription()
            

    def description(self):
        return {
            'name': 'Annotations',
            'maintainer': 'Jon Lauters',
            'maintainer_email': 'jon@epandda.org',
            'description': 'Returns openAnnotations for linked data in ePANDDA.',
            'params': [
                {
                    "name": "annotationDate",
                    "label": "Annotation Date",
                    "type": "text",
                    "required": False,
                    "description": "Filter annotation results by AnnotatedAt date. Format annotationDate=YYYY-MM-DD"
                }
            ]
        }
                
