class idigbio:
        def dbName(self):
                return "idigbio"

        def collectionName(self):
                return "occurrence"

        def availableFields(self):
                return ["id", "idigbio:barcodeValue", "dwc:basisOfRecord", "dwc:bed", "dwc:catalogNumber",
                        "dwc:class", "dwc:collectionCode", "dwc:collectionID", "idigbio:collectionName", "dwc:recordedBy",
                        "dwc:vernacularName", "dwc:continent", "dwc:coordinateUncertaintyInMeters", "dwc:country",
                        "idigbio:isoCountryCode",
                        "dwc:county", "dwc:eventDate", "idigbio:dateModified", "idigbio:dataQualityScore",
                        "dwc:earliestAgeOrLowestStage",
                        "dwc:earliestEpochOrLowestSeries", "dwc:earliestEraOrLowestErathem", "dwc:earliestPeriodOrLowestSystem",
                        "idigbio:etag",
                        "dwc:family", "dwc:fieldNumber", "idigbio:flags", "dwc:formation", "gbif:cannonicalName", "gbif:genus",
                        "gbif:specificEpithet",
                        "gbif:taxonID", "dwc:genus", "idigbio:geoPoint", "idigbio:geoShape", "dwc:group", "idigbio:hasImage",
                        "idigbio:hasMedia",
                        "dwc:higherClassification", "dwc:individualCount", "dwc:infraspecificEpithet", "dwc:institutionCode",
                        "dwc:institutionID",
                        "idigbio:institutionName", "dwc:kingdom", "dwc:latestAgeOrHighestStage",
                        "dwc:latestEpochOrHighestSeries", "dwc:latestEraOrHighestErathem",
                        "dwc:latestPeriodOrHighestSystem", "dwc:lithostratigraphicTerms", "dwc:locality",
                        "dwc:lowestBiostratigraphicZone", "dwc:maximumDepthInMeters",
                        "dwc:maximumElevationInMeters", "idigbio:mediarecords", "dwc:member", "dwc:minimumDepthInMeters",
                        "dwc:minimumElevationInMeters",
                        "dwc:municipality", "dwc:occurrenceID", "dwc:order", "dwc:phylum", "idigbio:recordIds",
                        "dwc:recordNumber", "idigbio:recordset",
                        "dwc:scientificName", "dwc:specificEpithet", "dwc:startDayOfYear", "dwc:stateProvince",
                        "dwc:typeStatus", "idigbio:uuid",
                        "dwc:verbatimEventDate", "dwc:verbatimLocality", "idigbio:version", "dwc:waterBody"]
