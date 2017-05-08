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

# Condense Classification Path into list of de-duplicated terms
cursor = db.pbdb_taxon_lookup.find().limit(5)
for record in cursor:

  condensed = condense_higher_taxa( record['classification_path'] )
  print "Taxon Lookup Condensed: "
  print condensed

  # Get pbdb_ref record based on ref_no => pid link
  ref_cursor = db.pbdb_refs.find({"pid": record['ref_no']})
  for ref in ref_cursor:

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

  
    # Condense sci_names
    for rs in ref['sci_names']:
      sci_name_parts = rs.split(" ")

      if sci_name_parts[0].lower() not in [x.lower() for x in record['genus']]:
        print "missing genus name"
        print sci_name_parts[0]
        print record['genus']  

      if sci_name_parts[1] and sci_name_parts[1].lower() not in [x.lower() for x in record['species']]:
        print "missing species name"


  # Condense states, counties
  if sorted(ref['states']) == sorted(record['states']):
    print "states match"
  else:
    print "states differ ..."
  

  # Condense authors


# Combine pbdb_refs, pubIndex, pbdb_taxon_lookup into single record

# Condense sci_names, states, counties, classification paths, DOIs, authors


