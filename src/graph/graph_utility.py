from rdflib import Graph, RDF, OWL
from rdflib.term import URIRef, Literal, Node, BNode
from typing import Union

restriction_type = [OWL.hasValue, OWL.someValuesFrom, OWL.allValuesFrom]
collection_type = {OWL.intersectionOf: ('Intersection', 'owl:intersectionOf'), OWL.unionOf: ('Union', 'owl:unionOf')}


def uri_or_literal_2label(node: Union[URIRef, Literal, Node, str]) -> str:
    if isinstance(node, Literal) or isinstance(node, BNode):
        return str(node)
    else:
        if '#' in str(node):
            return str(node).split('#')[-1]
        else:
            return str(node).split('/')[-1]


def recursive_pattern_matching(knowledge_graph: Graph, node: Node, result: []):
    for s, p, o in knowledge_graph.triples((node, None, None)):
        if p in collection_type or p in restriction_type or p == RDF.first or p == RDF.rest or p == OWL.onProperty:
            result.extend([[s, p, o]])
        recursive_pattern_matching(knowledge_graph, o, result)


def extract_property_value(knowledge_graph: Graph, node: Node):
    edge, n = None, None
    for s, p, o in knowledge_graph.triples((node, None, None)):
        if p == OWL.onProperty:
            edge = o
        if p in restriction_type and isinstance(o, URIRef) or isinstance(o, Literal):
            n = o

    return edge, n


def get_collection_type(property):
    return collection_type.get(property)
