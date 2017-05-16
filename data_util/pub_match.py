import idigbio
import codecs
import json
import requests
import pprint
from pymongo import MongoClient

# MongoDB setup
client = MongoClient('mongodb://127.0.0.1:27017')
db = client.test

# Python iDigBio Client
api = idigbio.json()

cursor = db.pubIndexV2.find()
for record in cursor:

  if 'genus' in record:
    print "States List: "
    print record['states']
  
    print "Genus List: "
    print record['genus']

    print "Species List: "
    print record['species']

    if 'author1_last' in record:
      print "First Author: "
      print record['author1_last']

    if 'author2_last' in record:
      print "Second Author: "
      print record['author2_last']

    if 'index_term' in record:
      print "Indexed Term: "
      print record['index_term']

    else: 

      # We should have this
      refs_cursor = db.pbdb_refs.find({"pid": record['pid']})
      for ref in refs_cursor:
     
        if 'title' in ref:
          print "updated pubindex with title"
          db.pubIndexV2.update({"_id": record['_id']}, {"$set": {"index_term": ref['title']}})

    record_list = []
    if record['states']:
      for state in record['states']:

        print " =================== "
        print " =================================="
        print " ===========================================\n\n\n\n\n"

        for genus in record['genus']:

          genus = genus.encode('utf-8')
          state = state.encode('utf-8')

          print "searching " + genus + " located in " + state    

          idb = requests.get('https://search.idigbio.org/v2/search/records/?rq={"genus": "' + genus + '", "stateprovince": "' + state + '"}')

          if 200 == idb.status_code:
            record_list = json.loads(idb.content)

            if record_list['items']:

              vett_ids = [ r['uuid'] for r in record_list['items'] ]

              print "Adding vettables to index record"
              db.pubIndexV2.update({"_id": record['_id']}, {"$set": {"needs_vetting": vett_ids }}) 

