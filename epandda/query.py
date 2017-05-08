from flask_restful import Resource, Api
from flask import current_app, url_for
from base import baseResource
import importlib

#
# Boolean
#
class query(baseResource):
    def process(self):

        query_list = self.getQueryList()

        queries = []
        for q in query_list:
            queries.append(q)

        return self.respond({
          'description': 'ePANDDA query endpoint',
          'routes': queries
        }, "routes")