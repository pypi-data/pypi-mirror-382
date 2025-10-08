import uuid

REQUIRED_DWCA_TERMS = {
    "Australia": ["scientificName", "eventDate", "basisOfRecord"], #occurrenceID, catalogNumber, recordNumber
    "ALA": ["scientificName", "eventDate", "basisOfRecord"],
}

ID_REQUIRED_DWCA_TERMS = {
    "Australia": ["occurrenceID", "catalogNumber", "recordNumber"], 
    "ALA": ["occurrenceID", "catalogNumber", "recordNumber"],
}

GEO_REQUIRED_DWCA_TERMS = {
    "Australia": ['decimalLatitude','decimalLongitude','geodeticDatum','coordinateUncertaintyInMeters'], #'coordinatePrecision'], 
    "ALA": ['decimalLatitude','decimalLongitude','geodeticDatum','coordinateUncertaintyInMeters'], #'coordinatePrecision'
}

NAME_MATCHING_TERMS = {
    "Australia": ["scientificName","scientificNameAuthorship","vernacularName","rank","species","genus","family","order","classs","phylum","kingdom"],
    "ALA": ["scientificName","scientificNameAuthorship","vernacularName","rank","species","genus","family","order","classs","phylum","kingdom"]
}

TAXON_TERMS = {
    "Australia": ["scientificName","vernacularName","genus","family","order","classs","phylum","kingdom"], #"rank","species",
    "ALA": ["scientificName","vernacularName","genus","family","order","classs","phylum","kingdom"] #"rank","species",
}
'''
        'records_with_taxonomy_count': 'records_with_taxonomy_count',
        'records_with_recorded_by_count': 'records_with_recorded_by_count',
'''

required_columns_event = [
    "eventDate",
    "parentEventID",
    "eventID",
    "Event",
    "samplingProtocol"
]

continents = ["Africa","Antarctica","Asia","Europe","North America","Oceania","South America"]

unique_messages = {
    'organismQuantity': 'The organismQuantity must be a string, and must give a quantity to measurement type.',
    'organismQuantityType': 'The organismQuantity must be a string, and must give context to the field organismQuantity.'
}

REPORT_TERMS = {
    "Australia": {
        'record_type': 'record_type',
        'record_count': 'record_count',
        'record_error_count': 'record_error_count',
        'errors': 'Errors',
        'warnings': 'Warnings',
        'all_required_columns_present': 'all_required_columns_present',
        'missing_columns': 'missing_columns',
        'column_counts': 'column_counts',
        'records_with_temporal_count': 'records_with_temporal_count',
        'taxonomy_report': 'taxonomy_report',
        'coordinates_report': 'coordinates_report',
        'datetime_report': 'datetime_report',
        'vocab_reports': 'vocab_reports',
        'incorrect_dwc_terms': 'incorrect_dwc_terms'
    }
}

formats = {
    str: 'str',
    int: 'int',
    float: 'float',
    bool: 'bool',
    uuid.UUID: 'uuid',
    uuid.SafeUUID: 'uuid',
    list: 'list'
}

# dict of words and check function
'''
terms_and_check_functions = {
    'check_abundance': ['individualCount','organismQuantity','organismQuantityType'],
    'check_collection': ['datasetID','datasetName','catalogNumber'],
    'check_coordinates': ['decimalLatitude','decimalLongitude','geodeticDatum','coordinateUncertaintyInMeters','coordinatePrecision'],
    'check_datetime': ['eventDate','year','month','day','eventTime'],
    'check_events': ['eventID','parentEventID','eventType','Event','samplingProtocol'],
    'check_individual_traits': ['individualID','lifeStage','sex','vitality','reproductiveCondition'],
    'check_license': ['license','rightsHolder','accessRights'],
    'check_locality': ['continent','country','countryCode','stateProvince','locality'],
    'check_observer': ['recordedBy','recordedByID'],
    'check_occurrences': ['basisOfRecord','occurrenceStatus','occurrenceID','catalogNumber','recordNumber'],
    'check_scientificName': ['scientificNameAuthorship','scientificNameRank','scientificName'],
    'check_taxonomy': ['kingdom','phylum','class','order','family','genus','specificEpithet','vernacularName'],
}
'''

terms_and_check_functions = {
    'individualCount': 'check_abundance',
    'organismQuantity': 'check_abundance',
    'organismQuantityType': 'check_abundance',
    'datasetID': 'check_collection',
    'datasetName': 'check_collection',
    'catalogNumber': 'check_collection',
    'decimalLatitude': 'check_coordinates',
    'decimalLongitude': 'check_coordinates',
    'geodeticDatum': 'check_coordinates',
    'coordinateUncertaintyInMeters': 'check_coordinates',
    'coordinatePrecision': 'check_coordinates',
    'eventDate': 'check_datetime',
    'year': 'check_datetime',
    'month': 'check_datetime',
    'day': 'check_datetime',
    'eventTime': 'check_datetime',
    'eventID': 'check_events',
    'parentEventID': 'check_events',
    'eventType': 'check_events',
    'Event': 'check_events',
    'samplingProtocol': 'check_events',
    'individualID': 'check_individual_traits',
    'lifeStage': 'check_individual_traits',
    'sex': 'check_individual_traits',
    'vitality': 'check_individual_traits',
    'reproductiveCondition': 'check_individual_traits',
    'license': 'check_license',
    'rightsHolder': 'check_license',
    'accessRights': 'check_license',
    'continent': 'check_locality',
    'country': 'check_locality',
    'countryCode': 'check_locality',
    'stateProvince': 'check_locality',
    'locality': 'check_locality',
    'recordedBy': 'check_observer',
    'recordedByID': 'check_observer',
    'basisOfRecord': 'check_occurrences',
    'occurrenceStatus': 'check_occurrences',
    'occurrenceID': 'check_occurrences',
    'catalogNumber': 'check_occurrences',
    'recordNumber': 'check_occurrences',
    'scientificNameAuthorship': 'check_scientificName',
    'scientificNameRank': 'check_scientificName',
    'scientificName': 'check_scientificName',
    'kingdom': 'check_taxonomy',
    'phylum': 'check_taxonomy',
    'class': 'check_taxonomy',
    'order': 'check_taxonomy',
    'family': 'check_taxonomy',
    'genus': 'check_taxonomy',
    'specificEpithet': 'check_taxonomy',
    'vernacularName': 'check_taxonomy',
}