from flask_restful import Resource, Api
from flask import current_app, url_for
import json

#
# Emit API banner
#
class show(Resource):
    def get(self):

        routes = []
        for rule in current_app.url_map.iter_rules():

          options = {}
          for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

          url = url_for(rule.endpoint, **options)
          routes.append({'url': url, 'methods': ",".join(rule.methods) }) 

        return {'success': {
                 'v': 1,
                 'description': 'this is the root of ePANDDA REST API',
                 'routes': routes 
               }}
