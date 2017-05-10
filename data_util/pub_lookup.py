import json
from pymongo import MongoClient

config = json.load(open('./config.json'))

# mongoDB setup
client = MongoClient(config['mongo_url'])
db = client.test

def condense_higher_taxa( classification_path ):
  higher_taxa = []
  
  if classification_path:
    for path in classification_path:

      path_parts = path.split("|")
      for part in path_parts:

        if part not in higher_taxa:
          higher_taxa.append( part )

  return higher_taxa


def getPubIndex( ref_title ):

  # TODO: figure out what we need to pass to link these ...  
  # Looks like index_term ?? 

  return {
	"_id" : "58ae0177336d30211d291adf",
	"index_term" : "\u0001 The Eocene expansion of nautilids to high latitudes",
	"author1_last" : "Dzik",
	"author2_init" : "A.",
	"author2_last" : "\u001d\u0015Gazdzicki",
	"doi" : "",
	"matching_data" : [ ],
	"author1_init" : "J."
  }
 



# Condense Classification Path into list of de-duplicated terms
cursor = db.pbdb_taxon_lookup.find({"ref_no": "56258"})
for record in cursor:

  master_record = {}


  condensed = condense_higher_taxa( record['classification_path'] )
  print "Taxon Lookup Condensed: "
  print condensed

  # Get pbdb_ref record based on ref_no => pid link
  ref_cursor = db.pbdb_refs.find({"pid": record['ref_no']})
  for ref in ref_cursor:

    # our combined record starts with PubIndex
    master_record = getPubIndex( ref['title'] )

    if 'classification_path' in ref:
      refs_condensed = condense_higher_taxa( ref['classification_path'] )
      print "refs_condensed"
      print refs_condensed

      if sorted(condensed) == sorted(refs_condensed):
        print "higher order taxa the same"
      else:
        print "higher order taxa differs ..."

        for rc in refs_condensed:
          if rc not in condensed:
            condensed.append( rc )

        print "Missing values added to condensed list ..."
    master_record['higher_taxa'] = condensed

  
    # Condense sci_names
    for rs in ref['sci_names']:
      sci_name_parts = rs.split(" ")

      master_record['genus'] = record['genus']
      master_record['species'] = record['species']

      if sci_name_parts[0].lower() not in [x.lower() for x in record['genus']]:
        print "missing genus name"
        print sci_name_parts[0]
        print record['genus']  

        master_record['genus'].append( sci_name_parts[0] )

      if sci_name_parts[1] and sci_name_parts[1].lower() not in [x.lower() for x in record['species']]:
        print "missing species name"
        master_record['species'].append( sci_name_parts[1] ) 


  master_record['pubtitle'] = ref['pubtitle']
  master_record['pubyear'] = ref['pubyear']
  master_record['issue'] = ref['issue']
  master_record['volume'] = ref['volume']

  # internal pbdb id links
  master_record['pid'] = ref['pid']
  master_record['linked_occurrences'] = record['occ_no']
  master_record['linked_collections'] = record['coll_no']

  # Condense states
  master_record['counties'] = ref['counties']
  master_record['countries'] = ref['countries']

  master_record['states'] = ref['states']
  if sorted(ref['states']) != sorted(record['states']):
    for st in record['states']:
      if st not in master_record['states']:
        master_record['states'].append( st )
  


print "Master Record:"
print master_record






# Condense sci_names, states, counties, classification paths, DOIs, authors


