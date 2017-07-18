import codecs
import json
import requests
import pprint
from pymongo import MongoClient

# MongoDB setup
client = MongoClient('mongodb://127.0.0.1:27017')
db = client.test

cursor = db.pubIndexV2.find({'vetted': {'$exists': False}})
for record in cursor:

   if 'needs_vetting' in record:
 
     print "We need to match .. "
     pprint.pprint( record )

     vetted = []
     for v in record['needs_vetting']:
        
        score = 0
        matched_fields = []

        idb = requests.get('https://search.idigbio.org/v2/view/records/' + str(v))
        if 200 == idb.status_code:
          idigbio = json.loads(idb.content)       

          pprint.pprint( idigbio['data'] )
          
          if idigbio['data']['dwc:stateProvince'].lower() in record['states']:
            
            score = score + 1
            matched_fields.append("State Name")

          if 'dwc:specificEpithet' in idigbio['data']:
            if idigbio['data']['dwc:specificEpithet'] in record['species']:

              score = score + 1
              matched_fields.append("Species => Specific Epithet")

          if idigbio['data']['dwc:genus'] in record['genus']:

            score = score + 1
            matched_fields.append("Genus Name")

          if 'higher_taxa' in record and 'dwc:class' in idigbio['data']:
            if idigbio['data']['dwc:class'] in record['higher_taxa']:

              score = score + 1
              matched_fields.append("Class in Higher Taxa")

          if 'dwc:earliestPeriodOrLowestSystem' in idigbio['data']:
            if idigbio['data']['dwc:earliestPeriodOrLowestSystem'] in record['index_term']:

              score = score + 1
              matched_fields.append("Earliest Period / Lowest System found in title")

          if 'dwc:earliestAgeOrLowestStage' in idigbio['data']:
            if idigbio['data']['dwc:earliestAgeOrLowestStage'] in record['index_term']:

              score = score + 1
              matched_fields.append("Earliest Age / Lowest Stage found in title")

          if 'dwc:earliestEpochOrLowestSeries' in idigbio['data']:
            if idigbio['data']['dwc:earliestEpochOrLowestSeries'] in record['index_term']:

              score = score + 1
              matched_fields.append("Earliest Epoch / Lowest Series found in title")

          if 'dwc:earliestEraOrLowestErathem' in idigbio['data']:
            if idigbio['data']['dwc:earliestEraOrLowestErathem'] in record['index_term']:

              score = score + 1
              matched_fields.append("Earliest Era / Lowest Erathem found in title")

          if 'dwc:associatedReferences' in idigbio['data']:
            if 'author1_last' in record:
              if record['author1_last'] in idigbio['data']['dwc:associatedReferences']:
            
                score = score + 1
                matched_fields.append("Author1 found in Assoc Refs")

            if 'author2_last' in record:
              if record['author2_last'] in idigbio['data']['dwc:associatedReferences']:

                score = score + 1
                matched_fields.append("Author2 found in Assoc Refs")

            if record['index_term'] in idigbio['data']['dwc:associatedReferences']:

              score = score + 1
              matched_fields.append("title found in Assoc Refs")


          if 'dwc:scientificNameAuthorship' in idigbio['data']:
            if 'author1_last' in record:
              if record['author1_last'] in idigbio['data']['dwc:scientificNameAuthorship']:
    
                score = score + 1
                matched_fields.append("Authorship1 Matched")

            if record['pubyear'] in idigbio['data']['dwc:scientificNameAuthorship']:
              
              score = score + 1
              matched_fields.append("Pubyear in SciNameAuthorship")

            if 'author2_last' in record:
              if record['author2_last'] in idigbio['data']['dwc:scientificNameAuthorship']:

                score = score + 1
                matched_fields.append("Authorship2 Matched")

          if 'dwc:Identification' in idigbio['data']:
            for ID in idigbio['data']['dwc:Identification']:

              if 'dwc:identificationReferences' in ID:

                if record['index_term'] in ID['dwc:identificationReferences']:
             
                  score = score + 5
                  matched_fields.append("Article Title found in IdentRefs")

          if 'dcterms:bibliographicCitation' in idigbio['data']:
        
            # Consider this your lucky day
            # Check article title, author, pub title

            if record['index_term'] in idigbio['data']['dcterms:bibliographicCitation']:

              score = score + 5
              matched_fields.append("Article title in biblioCitation")

            if record['pubtitle'] in idigbio['data']['dcterms:bibliographicCitation']:
        
              score = score + 5
              matched_fields.append("Pub Title in biblioCitation")

            if 'author1_last' in record:
              if record['author1_last'] in idigbio['data']['dcterms:bibliographicCitation']:
           
                score = score + 1
                matched_fields.append("Author1 in BiblioCitation")
 
            if 'author2_last' in record:
              if record['author2_last'] in idigbio['data']['dcterms:bibliographicCitation']:
 
                score = score + 1
                matched_fields.append("Author2 in BiblioCitation")


        print "How'd we do? --------------------------------------------------------------"
        print "Score: " + str(score)
        print "Matched On: "
        pprint.pprint( matched_fields )

        vetted.append({ "uuid": v, "score": score, "matched_on": matched_fields})

     db.pubIndexV2.update({"_id": record['_id']}, {"$set": {"vetted": vetted }}) 


