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

if __name__ == '__main__':
  app.run(host = '0.0.0.0')

