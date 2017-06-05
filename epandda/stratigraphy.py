from mongo import mongoBasedResource
from flask_restful import reqparse
import gridfs
import json

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
    def process(self):
    	# Mongodb index for localities
		sindex = self.client.endpoints.chronoStratIndex3
		# Mongodb gridFS instance
		grid = gridfs.GridFS(self.client.endpoints)                   

		# returns dictionary of params as defined in endpoint description
		# will throw exception if required param is not present
		params = self.getParams()
		# offset and limit returned as ints with default if not set
		offset = self.offset()
		limit = self.limit()

		if self.paramCount > 0:
			imageRes = None
			res = None
			criteria = {'endpoint': 'stratigraphy', 'parameters': {}, 'matchTerms': []}
			stratQuery = []
			for p in [{'stage': ['lowStage', 'highStage', 'upperChronostratigraphy.stage', 'lowerChronostratigraphy.stage']}, {'series': ['lowSeries', 'highSeries', 'upperChronostratigraphy.series', 'lowerChronostratigraphy.series']}, {'system': ['lowSystem', 'highSystem', 'upperChronostratigraphy.system', 'lowerChronostratigraphy.system']}, {'erathem': ['lowErathem', 'highErathem', 'upperChronostratigraphy.erathem', 'lowerChronostratigraphy.erathem']}]:
				val = p.keys()[0]
				if (params[val]):
					criteria['parameters'][val] = params[val]
					for field in p[val]:
						stratQuery.append({field: params[val]})
			if(params['chronostratigraphy']):
				criteria['parameters']['chronostratigraphy'] = params['chronostratigraphy']
				stratQuery.append({'$text': {'$search': '"' + params['chronostratigraphy'] + '"'}})

			if (len(stratQuery) == 0):
				return self.respondWithError({"GENERAL": "No valid parameters specified"})
			if len(stratQuery) > 0:
				res = sindex.find({'$or': stratQuery})
			d = []
			matches = {'idigbio': [], 'pbdb': []}
			idbCount = 0
			pbdbCount = 0
			if res:
				for i in res:
					temp_doc = {}
					for level in ['lowStage', 'highStage', 'lowSeries', 'highSeries', 'lowSystem', 'highSystem', 'lowErathem', 'highErathem', 'upperChronostratigraphy', 'lowerChronostratigraphy']:
						if level in i:
							temp_doc[level] = i[level]
					criteria['matchTerms'].append(temp_doc)
					
					if 'pbdbGridFile' in i:
						pbdbGrids = i['pbdbGridFile']
						for file in pbdbGrids:
							pbdb_doc = grid.get(file)
							pbdb_matches = json.loads(pbdb_doc.read())
							matches['pbdb'] = matches['pbdb'] + pbdb_matches

					if 'idbGridFile' in i:
						if type(i['idbGridFile']) is list:
							idbGrids = i['idbGridFile']
							for file in idbGrids:
								idb_doc = grid.get(file)
								idb_matches = json.loads(idb_doc.read())
								matches['idigbio'] = matches['idigbio'] + idb_matches
						else:
							idb_doc = grid.get(i['idbGridFile'])
							idb_matches = json.loads(idb_doc.read())
							matches['idigbio'] = matches['idigbio'] + idb_matches
			
			idbCount = len(matches['idigbio'])
			pbdbCount = len(matches['pbdb'])

			item = {'matches': {'idigbio': matches['idigbio'], 'pbdb': matches['pbdb']}}
			d.append(item)
			d = self.resolveReferences(d)
			counts = {'totalCount': idbCount + pbdbCount, 'idbCount': idbCount, 'pbdbCount': pbdbCount}

			d['pbdb_resolved'] = d['pbdb_resolved'][offset:limit]
			
			media = []
			if imageRes:
				for m in imageRes:
					images = m['media_uris']
					for image in images:
						media.append(image)
			return self.respond({'counts': counts, 'results': d, 'criteria': criteria, 'media': media})

		else:
			return self.respondWithDescription()
    
    def description(self):
		return {
			'name': 'Chronostratigraphic Name Index',
			'maintainer': 'Michael Benowitz',
			'maintainer_email': 'michael@epandda.org',
			'description': 'Returns specimens matchting chronostratigraphic terms',
			'params': [
			{
				"name": "chronostratigraphy",
				"label": "Chronostratigraphy Full Text",
				"type": "text",
				"required": False,
				"description": "Search on the a full chronostratigraphic hierarchy "
			},{
				"name": "stage",
				"label": "Stage/Age",
				"type": "text",
				"required": False,
				"description": "The chronostratigraphic Stage/Age. Searches both high/low"
			},{
				"name": "series",
				"label": "Series/Epoch",
				"type": "text",
				"required": False,
				"description": "The chronostratigraphic Series/Epoch. Searches both high/low"
			},{
				"name": "system",
				"label": "System/Period",
				"type": "text",
				"required": False,
				"description": "The chronostratigraphic System/Period. Searches both high/low"
			},{
				"name": "erathem",
				"label": "Erathem/Era",
				"type": "text",
				"required": False,
				"description": "The chronostratigraphic Erathem/Era. Searches both high/low"
			}]
		}
			
    
    '''
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

          resp = {'data': self.resolveReferences(d)}

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
	'''