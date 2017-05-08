from flask_restful import Resource, Api
from flask import current_app, url_for
from base import baseResource

#
# Emit API banner
#
class show(baseResource):
    def process(self):

        routes = []
        for rule in current_app.url_map.iter_rules():
          if (rule.endpoint == 'static'):
              continue

          options = {}
          for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

          url = url_for(rule.endpoint, **options)
          routes.append({'url': url, 'methods': ",".join(rule.methods) })

        return self.respond({
          'description': 'ePANDDA REST API guide',
          'routes': routes
        }, "routes")