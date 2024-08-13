from rdflib import Graph, RDF, OWL, RDFS
from rdflib.term import URIRef, Literal, Node, BNode
from typing import Union

from src.graph.types import is_cardinality, is_restriction, is_collection


def uri_or_literal_2label(knowledge_graph: Graph, node: Union[URIRef, Literal, Node, str]) -> str:
    soma_ns = "http://www.ease-crc.org/ont/SOMA.owl#"
    dul_ns = "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#"
    for label in knowledge_graph.objects(URIRef(node), RDFS.label):
        return str(label)

    if isinstance(node, Literal):
        return str(node)
    else:
        label = str(node)
        if soma_ns in label:
            label = label.replace(soma_ns, 'SOMA:')
        if dul_ns in label:
            label = label.replace(dul_ns, 'DUL:')
        if '#' in str(node):
            label = label.split('#')[-1]
            if '/' in label:
                label = label.split('/')[-1]
            return label
        else:
            return label.split('/')[-1]


def recursive_pattern_matching(knowledge_graph: Graph, node: Node, result: []):
    for s, p, o in knowledge_graph.triples((node, None, None)):
        if isinstance(p, URIRef) and is_cardinality(p) or is_collection(p) or is_restriction(
                p) or p == RDF.first or RDF.rest:
            result.extend([[s, p, o]])
        if isinstance(o, BNode):
            recursive_pattern_matching(knowledge_graph, o, result)