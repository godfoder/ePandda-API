import json
import os.path
from collections import OrderedDict
from flask import Response

config = json.load(open('./config.json'));

def response_handler(return_object):

  # Default Response
  resp = {
    "success": True,
    "v": config['version'],
  }

  # Default Mimetype with override handling
  mime_type = "application/json"
  if "mimetype" in return_object:
    mime_type = return_object['mimetype']

  # Default Status Code with override handling
  status_code = 200
  if "status_code" in return_object:
    status_code = return_object['status_code']

  if "data" in return_object:
    resp['data'] = return_object['data']

  if "endpoint_description" in return_object:
    resp['description'] = return_object['endpoint_description']

  if "params" in return_object:
    resp['params'] = return_object['params']

  # API Root
  if "routes" in return_object:
    resp['routes'] = return_object['routes']

  return Response(response=json.dumps(resp, sort_keys=True,indent=4, separators=(',', ': ')).encode('utf8'), status=status_code, mimetype=mime_type)