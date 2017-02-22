from flask_restful import Resource, Api

#
# Emit API banner
#
class show(Resource):
    def get(self):
        return {'v1': 'https://epandda.org/api/v1' }