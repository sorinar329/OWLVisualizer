from rdflib import Graph, RDF, OWL, RDFS
from rdflib.term import URIRef, Literal, Node, BNode
from typing import Union

from src.graph.types import is_cardinality, is_restriction, is_collection

task = URIRef('http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Task')
disposition = URIRef('http://www.ease-crc.org/ont/SOMA.owl#Disposition')
tool = URIRef('http://www.ease-crc.org/ont/food_cutting#Tool')


def uri_or_literal_2label(knowledge_graph: Graph, node: Union[URIRef, Literal, Node, str]) -> str:
    if isinstance(node, Literal):
        return str(node)
    else:
        if '#' in str(node):
            label = str(node).split('#')[-1]
            if '/' in label:
                label = label.split('/')[-1]
            return label
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
        if isinstance(p, URIRef) and is_restriction(p):
            n = o

    return edge, n


def extract_property_value2(knowledge_graph: Graph, node: Node):
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
            # edge = p
            cardinality = o
        if p == OWL.onProperty:
            edge = o
        if p == OWL.onClass:
            cls = o
    return edge, cardinality, cls


def get_all_actions_tasks(knowledge_graph: Graph, classes: set, parent_class=task):
    for triple in knowledge_graph.triples((None, RDFS.subClassOf, parent_class)):
        classes.add(str(triple[0]))
        classes.add(str(triple[2]))
        get_all_actions_tasks(knowledge_graph, classes, parent_class=triple[0])


def get_all_dispositions(knowledge_graph: Graph, classes: set, parent_class=disposition):
    for triple in knowledge_graph.triples((None, RDFS.subClassOf, parent_class)):
        classes.add(str(triple[0]))
        classes.add(str(triple[2]))
        get_all_dispositions(knowledge_graph, classes, triple[0])


def get_all_tools(knowledge_graph: Graph, classes: set, parent_class=tool):
    for triple in knowledge_graph.triples((None, RDFS.subClassOf, parent_class)):
        classes.add(str(triple[0]))
        classes.add(str(triple[2]))
        get_all_dispositions(knowledge_graph, classes, triple[0])
