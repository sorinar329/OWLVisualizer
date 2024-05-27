from rdflib import OWL, URIRef

cardinality_types = {OWL.qualifiedCardinality: 'exactly', OWL.minQualifiedCardinality: 'min',
                     OWL.maxQualifiedCardinality: 'max'}

restriction_type = {OWL.hasValue: 'value', OWL.someValuesFrom: 'some', OWL.allValuesFrom: 'only'}

collection_type = {OWL.intersectionOf: 'AND', OWL.unionOf: 'OR'}


def get_cardinality_name(p: URIRef):
    return cardinality_types.get(p)


def get_collection_name(p: URIRef):
    return collection_type.get(p)


def get_restriction_name(p: URIRef):
    return restriction_type.get(p)


def is_collection(p: URIRef):
    return p in collection_type


def is_restriction(p: URIRef):
    return p in restriction_type


def is_cardinality(p: URIRef):
    return p in cardinality_types
