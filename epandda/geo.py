from mongo import mongoBasedResource
from flask_restful import reqparse
import gridfs
import json
from bson import ObjectId


parser = reqparse.RequestParser()
parser.add_argument('locality', type=str, help='Locality name to to search geoname records by')

#
#
#
class geoname(mongoBasedResource):
    def process(self):
        # Mongodb index for localities
        lindex = self.client.test.localityIndex   

        # Mongodb gridFS instance
        grid = gridfs.GridFS(self.client.test)                   

        # returns dictionary of params as defined in endpoint description
        # will throw exception if required param is not present
        params = self.getParams()


        # offset and limit returned as ints with default if not set
        offset = self.offset()
        limit = self.limit()

        if self.paramCount > 0:
          criteria = {'endpoint': 'geoname', 'parameters': {}, 'matchTerms': {'stateProvinceNames': [], 'countryNames': [], 'countyNames': [], 'localityNames': [], 'originalStates': [], 'originalCountries': [], 'originalCounties': [], 'originalLocalities': []}}
          geoQuery = []

          for p in ['countryName', 'countryCode', 'locality', 'stateProvinceName', 'county']:
              if (params[p]):
                  criteria['parameters'][p] = params[p]
                  geoQuery.append({p: params[p]})

          if (len(geoQuery) == 0):
            return self.respondWithError({"GENERAL": "No parameters specified"})

          res = lindex.find({'$and': geoQuery})

          d = []
          matches = {'idigbio': [], 'pbdb': []}
          idbCount = 0
          pbdbCount = 0
          for i in res:
            if i['countryName'] not in criteria['matchTerms']['countryNames']:
              criteria['matchTerms']['countryNames'].append(i['countryName'])
            if i['stateProvinceName'] not in criteria['matchTerms']['stateProvinceNames']:
              criteria['matchTerms']['stateProvinceNames'].append(i['stateProvinceName'])
            if i['county'] not in criteria['matchTerms']['countyNames']:
              criteria['matchTerms']['countyNames'].append(i['county'])
            if 'locality' in i:
              if i['locality'] not in criteria['matchTerms']['localityNames']:
                criteria['matchTerms']['localityNames'].append(i['locality'])
            for origState in i['originalStateProvinceName']:
              if origState not in criteria['matchTerms']['originalStates']:
                criteria['matchTerms']['originalStates'].append(origState)
            for origCountry in i['originalCountryName']:
              if origCountry not in criteria['matchTerms']['originalCountries']:
                criteria['matchTerms']['originalCountries'].append(origCountry)
            for origCounty in i['original_county']:
              if origCounty not in criteria['matchTerms']['originalCounties']:
                criteria['matchTerms']['originalCounties'].append(origCounty)
            if 'original_locality' in i:
              for origLocality in i['original_locality']:
                if origCounty not in criteria['matchTerms']['originalLocalities']:
                  criteria['matchTerms']['originalLocalities'].append(origLocality)
            if 'pbdbGridFile' in i:
              pbdbGrid = i['pbdbGridFile']
              pbdb_doc = grid.get(pbdbGrid)
              pbdb_matches = json.loads(pbdb_doc.read())
              matches['pbdb'] = matches['pbdb'] + pbdb_matches
              pbdbCount += len(pbdb_matches)
            
            if 'idbGridFile' in i:
              idbGrid = i['idbGridFile']
              idb_doc = grid.get(idbGrid)
              idb_matches = json.loads(idb_doc.read())
              matches['idigbio'] = matches['idigbio'] + idb_matches
              idbCount += len(idb_matches)
              #terms = i['original_terms']
              #terms.append(locality)
              #item = {"terms": terms, "matches": {"pbdb": i['pbdb_data'], "idigbio": i['idb_data']}}
              #d.append(item)

          item = {'matches': matches}
          d.append(item)
          d = self.resolveReferences(d)
          #idb_count = len(d['idigbio_resolved'])
          #pbdb_count = len(d['pbdb_resolved'])
          counts = {'totalCount': idbCount + pbdbCount, 'idbCount': idbCount, 'pbdbCount': pbdbCount}

          
          d['pbdb_resolved'] = d['pbdb_resolved'][offset:limit]

          return self.respond({'counts': counts, 'results': d, 'criteria': criteria})

        else:
          return self.respondWithDescription()

    def description(self):
        return {
            'name': 'Geographic name/locality index',
            'maintainer': 'Michael Benowitz',
            'maintainer_email': 'michael@epandda.org',
            'description': 'Returns specimens collected from a given locality',
            'params': [
            {
                "name": "geolocation",
                "type": "text",
                "required": False,
                "description": "A generic place name, will search across locality, county, state/province and country fields"
            },
            {
                "name": "countryName",
                "type": "text",
                "required": False,
                "description": "Full country names"
            },
            {
                "name": "countryCode",
                "type": "text",
                "required": False,
                "description": "2-letter country code, provided from geonames.org"
            },
            {
                "name": "stateProvinceName",
                "type": "text",
                "required": False,
                "description": "State or province name. Do not include qualifiers (e.g. State, Province) to return better results"
            },
            {
                "name": "stateProvinceCode",
                "type": "text",
                "required": False,
                "description": "State or province name. Do not include qualifiers (e.g. State, Province) to return better results"
            },
            {
                "name": "county",
                "type": "text",
                "required": False,
                "description": 'County name. Do not add "County" to your search string'
            },
            {
                "name": "locality",
                "type": "text",
                "required": False,
                "description": "The specific locality where a specimen was recorded"
            },
            {
                "name": "geoPoint",
                "type": "text",
                "required": False,
                "description": "The Latitude, Longitude to search on. Provide a comma separated string"
            },
            {
                "name": "geoUncertainty",
                "type": "text",
                "required": False,
                "description": "The distance from the provided geoPoint to match specimens within. The distance provided will be used to draw a circle around the geoPoint"
            }
        ]}

