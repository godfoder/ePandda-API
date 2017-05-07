import json
import requests
import collections
import datetime
import time
import logging
import urllib
from functools import wraps, update_wrapper
from flask import Flask, request, current_app, make_response, session, escape, Response
from flask_restful import Resource, Api
from werkzeug.security import safe_str_cmp

from epandda import banner
from epandda import geo
from epandda import stats
from epandda import publication
from epandda import strat
from epandda import occ


config = json.load(open('./config.json'));

# Init
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = config['auth_secret']
api = Api(app)


# emit banner
api.add_resource(banner.show, '/')
api.add_resource(geo.geoname, '/geoname')
api.add_resource(stats.stats, '/stats')
api.add_resource(publication.pubs, '/publication')
api.add_resource(strat.stratigraphy, '/stratigraphy')
api.add_resource(occ.occurrences, '/occurrence')

if __name__ == '__main__':
  app.run()
