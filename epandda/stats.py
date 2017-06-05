from flask_restful import Resource, Api
from base import baseResource
#
# Emit API stats
#
class stats(baseResource):
    def process(self):
        
        localityFields = {'localities': 'originalLocality', 'counties': 'county', 'stateProvinces': 'stateProvinceName', 'countries': 'countryName'}
        # Get any supplied parameters
        # There are no required parameters at this time 
        params = self.getParams()
        if self.paramCount > 0:
            criteria = {'endpoint': 'stats', 'parameters': []}
            pbdb = self.client.pbdb
            idb = self.client.idigbio
            endpoints = self.client.endpoints
            response = {}
            if params['totalRecords']:
                pbdbIndex = pbdb.pbdb_occurrences
                idbIndex = idb.occurrence
                pbdbCount = pbdbIndex.find().count()
                idbCount = idbIndex.find().count()
                totalCount = pbdbCount + idbCount
                criteria['parameters'].append('totalRecords')
                response['totalRecords'] = totalCount
                response['specimens'] = idbCount
                response['occurrences'] = pbdbCount
           
            localityIndex = endpoints.localityIndexV3
            for place in ['countries', 'stateProvinces', 'counties', 'localities']:
            	if params[place]:
            		placeTerm = localityFields[place]
            		#placeCount = len(list(localityIndex.aggregate([{'$group': {'_id': {'localities': '$' + placeTerm}}}])))
                	placeCount = localityIndex.count()
                	criteria['parameters'].append(place)
                	response[place] = placeCount

            if params['geoPoints']:
                geoPointIndex = endpoints.geoPointIndex2
                geoCount = geoPointIndex.find().count()
                criteria['parameters'].append('geoPoints')
                response['geoPoints'] = geoCount
           		
            if params['taxonomies']:
                taxonIndex = endpoints.taxonIndex2
                taxonCount = taxonIndex.find().count()
                criteria['parameters'].append('taxonomies')
                response['taxonomies'] = taxonCount
        else:
          return self.respondWithDescription()
        # Indexes for querying stats from
        # TODO: Cache these results
        return self.respond({'results': response, 'criteria': criteria})

    def description(self):
        return {
            'name': 'API statistics',
            'maintainer': 'Michael Benowitz',
            'maintainer_email': 'michael@epandda.org',
            'description': '(Sometimes) interesting API statistics',
            'params': [
            {
                "name": "stateProvinces",
                "type": "boolean",
                "required": False,
                "description": "The number of unique states represented in the collections"
            },
            {
                "name": "countries",
                "type": "boolean",
                "required": False,
                "description": "The number of unique countries represented in the collections"
            },
            {
                "name": "counties",
                "type": "boolean",
                "required": False,
                "description": "The number of unique counties represented in the collections"
            },
            {
                "name": "localities",
                "type": "boolean",
                "required": False,
                "description": "The number of unique localities represented in the collections"
            },
            {
                "name": "geoPoints",
                "type": "boolean",
                "required": False,
                "description": "The number of unique geographic coordinates represented in the collections"
            },
            {
                "name": "totalRecords",
                "type": "boolean",
                "required": False,
                "description": "The count of all specimen/occurrence records included in project from iDigBio and PBDB"
            },
            {
                "name": "taxonomies",
                "type": "boolean",
                "required": False,
                "description": "The number of unique taxonomic hierarchies represented in the collections"
            },
            {
                "name": "geoPoints",
                "type": "boolean",
                "required": False,
                "description": "The number of unique geographic coordinates represented in the collections"
            }
            ]
        }