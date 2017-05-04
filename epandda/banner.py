from flask_restful import Resource, Api
from flask import current_app, url_for
from response_handler import response_handler

#
# Emit API banner
#
class show(Resource):
    def get(self):

        routes = []
        for rule in current_app.url_map.iter_rules():
          if (rule.endpoint == 'static'):
              continue

          options = {}
          for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

          url = url_for(rule.endpoint, **options)
          routes.append({'url': url, 'methods': ",".join(rule.methods) })

        resp = {
          'endpoint_description': 'ePANDDA REST API guide',
          'routes': routes,
        }

        return response_handler( resp )
        
