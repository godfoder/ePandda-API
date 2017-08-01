# ePANDDA Open Annotation Implementation
#
# @author: Jon Lauters
#
# Simple function to fascilitate construction of annotations for ePANDDA and iDigBio Consumption

import json
import time
import datetime
import uuid

def create(target, body):

  # Timestamp and annotation uuid
  anno_uuid = uuid.uuid4()
  datestamp = datetime.datetime.fromtimestamp( time.time() ).strftime('%Y-%m-%d %H:%M:%S %Z')

  target_uuid = str(target['uuid'])

  open_annotation = {}
  open_annotation['@context'] = ["https://www.w3.org/ns/oa.jsonld", {"dwc": "http://rs.tdwg.org/dwc/terms/"}] 
  open_annotation['@id'] = "urn:uuid:" + str(anno_uuid)
  open_annotation['@type'] = "oa:Annotation"
  open_annotation['annotatedAt'] = str(datestamp)
  open_annotation['annotatedBy'] = {
    "@id": "https://epandda.org", 
    "@type": "foaf:Project",
    "name": "ePANDDA Annotation Bot"
  }

  matchedOn = ''
  if body['matchedOn'] is not None:
    matchedOn = body['matchedOn']

  pbdb_id = ''
  if body['pbdb_id'] is not None:
    pbdb_id = body['pbdb_id']

  open_annotation['hasBody'] = {
    "! cnt:chars": matchedOn,
    "@id": "https://paleobiodb.org/data1.2/refs/single.json?id=" + pbdb_id + "&show=both",
    "@type": ["dwc:Occurrence", "cnt:ContentAsText"],
    "dc:format": "application/json"
  }

  open_annotation['hasTarget'] = {
    "@id": "urn:uuid:" + target_uuid,
    "@type": "oa:SpecificResource",
    "hasSource": { "@id" : "http://search.idigbio.org/v2/view/records/" + target_uuid }
  }

  return open_annotation
