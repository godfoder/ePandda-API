from mongo import mongoBasedResource
from response_handler import response_handler
from flask_restful import reqparse
import datetime
import gridfs
import json
from bson import ObjectId
parser = reqparse.RequestParser()

parser.add_argument('locality', type=str, help='Locality name to to search geoname records by')

#
#
#
class geoname(mongoBasedResource):
    def get(self):
        # Mongodb index for localities
        lindex = self.client.test.localityIndex   

        # Mongodb gridFS instance
        grid = gridfs.GridFS(self.client.test)                   

        # Parameters
        # required
        # NONE

        # optional (at least one is necessary)
        geolocation = self.getRequest().args.get('geolocation')
        countryName = self.getRequest().args.get('countryName')
        countryCode = self.getRequest().args.get('countryCode')
        stateProvinceName = self.getRequest().args.get('stateProvinceName')
        stateProvinceCode = self.getRequest().args.get('stateProvinceCode')
        county = self.getRequest().args.get('county')
        locality = self.getRequest().args.get('locality')
        geoPoint = self.getRequest().args.get('geoPoint')
        geoUncertainty = self.getRequest().args.get('geoUncertainty')

        offset = self.getRequest().args.get('offset')
        limit = self.getRequest().args.get('limit') 

        params = [
          {
            "name": "geolocation",
            "type": "text",
            "value": geolocation,
            "required": False,
            "description": "A generic place name, will search across locality, county, state/province and country fields"
          },
          {
            "name": "countryName",
            "type": "text",
            "value": countryName,
            "required": False,
            "description": "Full country names"
          },
          {
            "name": "countryCode",
            "type": "text",
            "value": countryCode,
            "required": False,
            "description": "2-letter country code, provided from geonames.org"
          },
          {
            "name": "stateProvince",
            "type": "text",
            "value": stateProvinceName,
            "required": False,
            "description": "State or province name. Do not include qualifiers (e.g. State, Province) to return better results"
          },
          {
            "name": "stateProvinceCode",
            "type": "text",
            "value": stateProvinceCode,
            "required": False,
            "description": "State or province name. Do not include qualifiers (e.g. State, Province) to return better results"
          },
          {
            "name": "county",
            "type": "text",
            "value": county,
            "required": False,
            "description": 'County name. Do not add "County" to your search string'
          },
          {
            "name": "locality",
            "type": "text",
            "value": locality,
            "required": False,
            "description": "The specific locality where a specimen was recorded"
          },
          {
            "name": "geoPoint",
            "type": "text",
            "value": geoPoint,
            "required": False,
            "description": "The Latitude, Longitude to search on. Provide a comma separated string"
          },
          {
            "name": "geoUncertainty",
            "type": "text",
            "value": geoUncertainty,
            "required": False,
            "description": "The distance from the provided geoPoint to match specimens within. The distance provided will be used to draw a circle around the geoPoint"
          }
        ]

        if len(self.getRequest().args) > 0:
          criteria = {'endpoint': 'geoname', 'parameters': {}, 'matchTerms': {'stateProvinceNames': [], 'countryNames': [], 'countyNames': [], 'originalStates': [], 'originalCountries': [], 'originalCounties': []}}
          geoQuery = []
          if locality:
            criteria['parameters']['locality'] = locality
            geoQuery.append({"$text": {"$search": locality}})
          if stateProvinceName:
            criteria['parameters']['stateProvinceName'] = stateProvinceName
            geoQuery.append({'stateProvinceName': stateProvinceName})
          if countryName:
            criteria['parameters']['countryName'] = countryName
            geoQuery.append({'countryName': countryName})
          if countryCode:
            criteria['parameters']['countryCode'] = countryCode
            geoQuery.append({'countryCode': countryCode})
          if county:
            criteria['parameters']['county'] = county
            geoQuery.append({'county': county})
          if not limit:
              limit = None
          if not offset:
              offset = 0
          #res = lindex.find({"$text": {"$search": locality}})
          res = lindex.find({'$and': geoQuery})

          d = []
          matches = {'idigbio': [], 'pbdb': []}
          total_count = 0
          for i in res:
            if i['countryName'] not in criteria['matchTerms']['countryNames']:
              criteria['matchTerms']['countryNames'].append(i['countryName'])
            if i['stateProvinceName'] not in criteria['matchTerms']['stateProvinceNames']:
              criteria['matchTerms']['stateProvinceNames'].append(i['stateProvinceName'])
            if i['county'] not in criteria['matchTerms']['countyNames']:
              criteria['matchTerms']['countyNames'].append(i['county'])
            for origState in i['originalStateProvinceName']:
              if origState not in criteria['matchTerms']['originalStates']:
                criteria['matchTerms']['originalStates'].append(origState)
            for origCountry in i['originalCountryName']:
              if origCountry not in criteria['matchTerms']['originalCountries']:
                criteria['matchTerms']['originalCountries'].append(origCountry)
            for origCounty in i['original_county']:
              if origCounty not in criteria['matchTerms']['originalCounties']:
                criteria['matchTerms']['originalCounties'].append(origCounty)
            gridInstance = i['pbdbGridFile']
            grid_doc = grid.get(gridInstance)
            grid_matches = json.loads(grid_doc.read())
            total_count += len(grid_matches)
            matches['pbdb'] = matches['pbdb'] + grid_matches
              #terms = i['original_terms']
              #terms.append(locality)
              #item = {"terms": terms, "matches": {"pbdb": i['pbdb_data'], "idigbio": i['idb_data']}}
              #d.append(item)

          item = {'matches': matches}
          d.append(item)
          d = self.resolveReferences(d)
          #idb_count = len(d['idigbio_resolved'])
          #pbdb_count = len(d['pbdb_resolved'])
          #counts = {'totalCount': idb_count + pbdb_count, 'idbCount': idb_count, 'pbdbCount': pbdb_count}

          
          d['pbdb_resolved'] = d['pbdb_resolved'][offset:limit]
          #resp = self.toJson({'totalCount': counts, 'timeReturned':  str(datetime.datetime.now()), 'limit': limit, 'offset': offset, 'specimenData': False, 'includeAnnotations': False, 'results': grid_doc, 'criteria': criteria})
          resp = self.toJson({'totalCount': total_count, 'timeReturned':  str(datetime.datetime.now()), 'limit': limit, 'offset': offset, 'specimenData': False, 'includeAnnotations': False, 'results': d, 'criteria': criteria})
          return resp

        else:

          resp = {
            'endpoint_description': 'Returns specimens collected from a given locality',
            'params': params
          }
          


        return resp

    def post(self):
      args = parser.parse_args()
  
      resp = {
        'endpoint_description': 'Returns geoname records',
        'params': args
      }

      return resp 
