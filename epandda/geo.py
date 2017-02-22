from mongo import mongoBasedResource

#
#
#
class geoname(mongoBasedResource):
    def get(self):
        locality = self.getRequest().args.get('locality')       # param
        lindex = self.client.test.spIndex                       # Mongodb index for localities

        res = lindex.find({"$text": {"$search": locality}})

        d = []
        for i in res:
            terms = i['original_terms']
            terms.append(locality)
            item = {"terms": terms, "matches": {"pbdb": i['pbdb_data'], "idigbio": i['idb_data']}}
            d.append(item)

        d = self.resolveReferences(d)
        resp = self.toJson(d)

        return resp
