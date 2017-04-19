from flask_restful import Resource, Api

#
# Emit API stats
#
class stats(Resource):
    def get(self):

        return {'stats': 'various counts for website coming soon ...'}
