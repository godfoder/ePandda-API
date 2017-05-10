from mongo import mongoBasedResource
from flask_restful import reqparse

parser = reqparse.RequestParser()

# Add Arguments (params) to parser here ...
parser.add_argument('scientific_name', type=str, help='Taxonomic name to search occurrences for')
parser.add_argument('locality', type=str, help='Locality name to filter taxonomic occurrences by')
parser.add_argument('period', type=str, help='The geologic time period to filter taxonomic occurrences by')
parser.add_argument('institution_code', type=str, help='The abbreviated code submitted by data provider to filter taxonomic occurrences by')

#
#
#
class occurrences(mongoBasedResource):
    def process(self):

        # required
        taxon_name = self.getRequest().args.get('taxon_name')   # param

        # optional
        locality   = self.getRequest().args.get('locality')       # param
        period     = self.getRequest().args.get('period')
        inst_code  = self.getRequest().args.get('institution_code')


        # TODO: use occ Index
        lindex = self.client.test.spIndex                       # Mongodb index for localities

        if taxon_name:

            # TODO: update for Occurrences

            res = lindex.find({"$text": {"$search": locality}})

            d = []
            for i in res:
                terms = i['original_terms']
                terms.append(locality)
                item = {"terms": terms, "matches": {"pbdb": i['pbdb_data'], "idigbio": i['idb_data']}}
                d.append(item)

            return self.respond(self.resolveReferences(d))
        else:
            return self.respondWithDescription()


    def description(self):
        return {
            'name': 'Occurrence index',
            'maintainer': 'Michael Benowitz',
            'maintainer_email': 'michael@epandda.org',
            'description': 'Returns specimens collected from a given locality',
            'params': [
                {
                    "name": "taxon_name",
                    "type": "text",
                    "required": True,
                    "description": "The taxa to search occurrences for"
                },
                {
                    "name": "locality",
                    "type": "text",
                    "required": False,
                    "description": "The locality name to bound taxonomic occurences to",
                },
                {
                    "name": "period",
                    "type": "text",
                    "description": "The geologic time period to filter taxon occurrences by"
                },
                {
                    "name": "institution_code",
                    "type": "text",
                    "char_limit": "TBD",
                    "description": "The abbreviated institution code that houses the taxon occurrence specimen"
                }
            ]}