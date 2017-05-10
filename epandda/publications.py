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

        # Required
        scientific_name = self.getRequest().args.get('scientific_name')

        # Optional
        journal         = self.getRequest().args.get('journal')
        article         = self.getRequest().args.get('article')
        author          = self.getRequest().args.get('author')
        state_prov      = self.getRequest().args.get('state_province')
        county          = self.getRequest().args.get('county')
        locality        = self.getRequest().args.get('locality')


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
            return self.respondWithDescription()

    def description(self):
        return {
            'name': 'Publication index',
            'maintainer': 'Jon Lauters',
            'maintainer_email': 'jon@epandda.org',
            'description': 'Returns specimen occurrence and publication records for a given scientific name. results can be filtered by the optional params',
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