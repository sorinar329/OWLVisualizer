from rdflib import Graph, RDF, OWL, RDFS
from rdflib.term import URIRef, Literal, Node, BNode
from typing import Union

from src.graph.types import is_cardinality, is_restriction, is_collection


def uri_or_literal_2label(knowledge_graph: Graph, node: Union[URIRef, Literal, Node, str]) -> str:
    for label in knowledge_graph.objects(node, RDFS.label):
        return f"'{label}'"

    if isinstance(node, Literal) or isinstance(node, BNode):
        return str(node)
    else:
        if '#' in str(node):
            return str(node).split('#')[-1]
        else:
            return str(node).split('/')[-1]


def recursive_pattern_matching(knowledge_graph: Graph, node: Node, result: []):
    for s, p, o in knowledge_graph.triples((node, None, None)):
        if isinstance(p, URIRef) and is_cardinality(p) or is_collection(p) or is_restriction(p) or p == RDF.first:
            result.extend([[s, p, o]])
        if isinstance(o, BNode):
            recursive_pattern_matching(knowledge_graph, o, result)


def extract_property_value(knowledge_graph: Graph, node: Node):
    edge, n = None, None
    for s, p, o in knowledge_graph.triples((node, None, None)):
        if p == OWL.onProperty:
            edge = o
        if is_restriction(p) and isinstance(o, URIRef) or isinstance(o, Literal):
            n = o

    return edge, n


def extract_cardinality_types(knowledge_graph: Graph, node: Node):
    edge, cardinality, cls = None, None, None
    for s, p, o in knowledge_graph.triples((node, None, None)):
        if is_cardinality(p):
            edge = p
            cardinality = o
        if p == OWL.onClass:
            cls = o
    return edge, cardinality, cls
