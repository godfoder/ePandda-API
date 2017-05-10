from flask_restful import Resource, Api

#
# Emit API stats
#
class stats(Resource):
    def process(self):

        return {'stats': 'API coverage and usage statistics'}

    def description(self):
        return {
            'name': 'API statistics',
            'maintainer': 'Michael Benowitz',
            'maintainer_email': 'michael@epandda.org',
            'description': 'Returns general API statistical information',
            'params': []
        }