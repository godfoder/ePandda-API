from mongo import mongoBasedResource
from flask_restful import reqparse

parser = reqparse.RequestParser()

parser.add_argument('scientific_name', type=str, help='Taxonomic name to search bibliographic records for')
parser.add_argument('journal', type=str, help='Journal name where taxon was described')
parser.add_argument('article', type=str, help='Article name where taxon was described')
parser.add_argument('author', type=str, help='One of the authors of article describing taxon')
parser.add_argument('state_province', type=str, help='State or province name to filter described taxon results')
parser.add_argument('county', type=str, help='County name to filter described taxon results')
parser.add_argument('locality', type=str, help='Locality name to filter described taxon results')

#
#
#
class publications(mongoBasedResource):
    def process(self):

        # Mongodb index for Publications
        pubIndex = self.client.endpoints.pubIndexV2

  
        # returns dictionary of params as defined in endpoint description
        # will throw exception if required param is not present
        params = self.getParams()

        # offset and limit returned as ints with default if not set
        offset = self.offset()
        limit = self.limit()

        if limit < 1:
          limit = 100

        if self.paramCount > 0:
          criteria = {
            'endpoint': 'publication',
            'parameters': {},
            'matchPoints': [],
            'matchTerms': { 
              'stateProvinceNames': [],
              'countryNames': [],
              'countyNames': [],
              'localityNames': [],
              'originalStates': [],
              'originalCountries': [],
              'originalCounties': [],
              'originalLocalities': []
            }
          }

          for p in ['countryName', 'countryCode', 'locality', 'stateProvinceName', 'stateProvinceCode', 'county']:
            if (params[p]):
              criteria['parameters'][p] = params[p]

          d = []
          matches = {'idigbio': [], 'pbdb': []}
          idbCount = 0
          pbdbCount = 0

          print "PARAMS CHECK: "
          print params

          res = pubIndex.find( pubQuery ) 

          if res:
            for i in res:
              if 'countryName' in i and i['countryName'] not in criteria['matchTerms']['countryNames']:
                criteria['matchTerms']['countryNames'].append(i['countryName'])

              if 'stateProvinceName' in i and i['stateProvinceName'] not in criteria['matchTerms']['stateProvinceNames']:
                criteria['matchTerms']['stateProvinceNames'].append(i['stateProvinceName'])
    
              if 'county' in i and i['county'] not in criteria['matchTerms']['countyNames']:
                criteria['matchTerms']['countyNames'].append(i['county'])
          
              if 'locality' in i:
                if i['locality'] not in criteria['matchTerms']['localityNames']:
                  criteria['matchTerms']['localityNames'].append(i['locality'])    

          
              if 'originalStateProvinceName' in i:
                for origState in i['originalStateProvinceName']:
                  if origState not in criteria['matchTerms']['originalStates']:
                    criteria['matchTerms']['originialStates'].append(origState)

              if 'originalCountryName' in i:
                for origCountry in i['originalCountryName']:
                  if origCountry not in criteria['matchTerms']['originalCountries']:
                    criteria['matchTerms']['originalContries'].append(origCountry)

              if 'original_county' in i:
                for origCounty in i['original_county']:
                  if origCounty not in criteria['matchTerms']['originalCounties']:
                    criteria['matchTerms']['originalCounties'].append(origCounty)

              if 'original_locality' in i:
                for origLocality in i['original_locality']:
                  if origLocality not in criteria['matchTerms']['originalLocalities']:
                    criteria['matchTerms']['originalLocalities'].append(origLocality)

          finalMatches = {'idigbio': [], 'pbdb': []}
          if len(matches['idigbio']) > 0:
            finalMatches['idigbio'] = set(matches['idigbio'])
          else:
            finalMatches['idigbio'] = matches['idigbio']

          idbCount = len(finalMatches['idigbio'])

          if len(matches['pbdb']) > 0:
            finalMatches = set(matches['pbdb'])
          else:
            finalMatches = matches['pbdb']

          pbdbCount = len(finalMatches['pbdb'])
          resolveSet = { 'idigbio': finalMatches['idigbio'][offset:limit],
                         'pbdb': finalMatches['pbdb'][offset:limit] }
          item = {'matches': finalMatches}
          d.append(item)
          d = self.resolveReferences(d)

          counts = {
            'totalCount': idbCount + pbdbCount, 
            'idbCount': idbCount,
            'pbdbCount': pbdbCount
          }

          return self.respond({'counts': counts, 'results': d, 'criteria': criteria})
        else:
          return self.respondWithDescription()
            

    def description(self):
        return {
            'name': 'Publication index',
            'maintainer': 'Jon Lauters',
            'maintainer_email': 'jon@epandda.org',
            'description': 'Returns specimen occurrence and publication records for a given scientific name. Results may be filtered using the available parameters.',
            'params': [
                {
                    "name": "scientific_name",
                    "type": "text",
                    "required": True,
                    "description": "Taxon to search occurrence records for"
                },
                {
                    "name": "journal",
                    "type": "text",
                    "required": False,
                    "description": "Then name of academic Journal a publication would be found"
                },
                {
                    "name": "article",
                    "type": "text",
                    "required": False,
                    "description": "The name of the journal article the given scientific_name appears in"
                },
                {
                    "name": "author",
                    "type": "text",
                    "required": False,
                    "description": "The name of the author who's article describes the given scientific_name"
                },
                {
                    "name": "state_province",
                    "type": "text",
                    "required": False,
                    "description": "The state/province to search for scientific_name and publication references"
                },
                {
                    "name": "county",
                    "type": "text",
                    "required": False,
                    "description": "The county to search for scientific_name and publication references"
                },
                {
                    "name": "locality",
                    "type": "text",
                    "required": False,
                    "description": "The locality name to search for scientific_name occurences and publication references"
                }
            ]}
