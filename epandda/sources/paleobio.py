class paleobio:
    def dbName(self):
        return "test"

    def collectionName(self):
        return "pbdb_flat_index"

    def availableFields(self):
        return ["interval_no", "paleolat", "species_name", "author1last", "collectors", "occurrence_no", "reference_no",
                "interval_name", "county", "taxon_name", "collection_type", "common_name", "type_specimen", "lng",
                "otherauthors", "period_max",
                "subgenus_name", "author2init", "pubno", "museum", "state", "comments", "member", "eml_interval",
                "reftitle", "taxon_rank", "abund_unit",
                "paleolng", "collection_aka", "epoch_min", "epoch_max", "pubtitle", "genus_name", "formation", "lat",
                "abund_value", "period_min", "doi",
                "catalog_number", "collection_no", "collection_name", "pubyr", "author1init", "intage_max", "taxon_no",
                "country", "author2last", "pubvol",
                "intage_min"]
