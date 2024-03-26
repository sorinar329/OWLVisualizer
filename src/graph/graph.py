from rdflib import Graph, OWL, RDFS, RDF
from rdflib.term import BNode, URIRef, Literal
from src.graph.graph_utility import recursive_pattern_matching, extract_property_value, uri_or_literal_2label, \
    extract_cardinality_types
from src.graph.types import get_cardinality_name, get_collection_name, is_restriction, \
    is_cardinality, is_collection
import random

knowledge_graph = Graph()
knowledge_graph.parse("data/mixing.owl")

graph_to_visualize = {'nodes': [], 'edges': []}


def get_all_classes(kg: Graph):
    nodes = set()
    for subclass, superclass in kg.subject_objects(RDFS.subClassOf):
        if isinstance(superclass, BNode):
            continue
        nodes.add(subclass)
        nodes.add(subclass)
        graph_to_visualize.get("edges").append({'from': str(subclass), 'to': str(superclass), 'label': 'subClassOf'})
    for node in nodes:
        graph_to_visualize.get("nodes").append({'id': str(node), 'label': uri_or_literal_2label(kg, node)})


def get_class_restrictions2(knowledge_graph):
    classes_with_restrictions = [[s, p, o] for (s, p, o)
                                 in knowledge_graph.triples((None, RDFS.subClassOf, None))
                                 if isinstance(o, BNode)]
    classes_with_restrictions.extend([[s, p, o] for (s, p, o)
                                      in knowledge_graph.triples((None, OWL.equivalentClass, None))
                                      if isinstance(o, BNode)])
    grouped_triples = []

    for s, p, o in classes_with_restrictions:
        triples = [[s, p, o]]
        recursive_pattern_matching(knowledge_graph, o, triples)

        grouped_triples.append(triples)
    collection_idx = 0

    for group in grouped_triples:
        parent_node, edge, child_node = '', '', ''
        for s, p, o in group:
            if p == RDFS.subClassOf or p == OWL.equivalentClass:
                parent_node = str(s)
                edge = uri_or_literal_2label(knowledge_graph, p)
            elif is_restriction(p):
                e, n = extract_property_value(knowledge_graph, s)
                if e is not None and n is not None:
                    child_node = n
                    child_label = uri_or_literal_2label(knowledge_graph, child_node)
                    edge += f'/{uri_or_literal_2label(knowledge_graph, e)}'
                    if edge[0] == '/':
                        edge = edge[1:]
                    child_node = f'{child_node}_{random.randint(0, 1000000000000)}'
                    graph_to_visualize.get("nodes").append({'id': child_node, 'label': child_label})
                    graph_to_visualize.get("edges").append({'from': child_node, 'to': parent_node,
                                                            'label': edge})
                    edge = ''
                else:
                    edge += f'/{uri_or_literal_2label(knowledge_graph, e)}'
                    edge += f'/{uri_or_literal_2label(knowledge_graph, p)}'
            elif is_cardinality(p):
                cardinality_property, cardinality, cls = extract_cardinality_types(knowledge_graph, s)
                edge += f'{get_cardinality_name(cardinality_property)} {cardinality}'
                child_label = uri_or_literal_2label(knowledge_graph, cls)
                if edge[0] == '/':
                    edge = edge[1:]
                child_node = f'{cls}_{random.randint(0, 1000000000000)}'
                graph_to_visualize.get("nodes").append({'id': child_node, 'label': child_label})
                graph_to_visualize.get("edges").append({'from': child_node, 'to': parent_node,
                                                        'label': edge})
                edge = ''
            elif is_collection(p):
                name = get_collection_name(p)
                child_node = f'{name}-{collection_idx}'
                collection_idx += 1
                edge += f'/{uri_or_literal_2label(knowledge_graph, p)}'
                graph_to_visualize.get("nodes").append({'id': child_node, 'label': child_node})
                graph_to_visualize.get("edges").append({'from': child_node, 'to': parent_node,
                                                        'label': edge})
                parent_node = child_node
                edge = ''
            elif p == RDF.first and isinstance(o, URIRef) or isinstance(o, Literal):
                edge, child_node = '', o
                child_label = uri_or_literal_2label(knowledge_graph, child_node)
                child_node = f'{child_node}_{random.randint(0, 1000000000000)}'
                graph_to_visualize.get("nodes").append({'id': child_node, 'label': child_label})
                graph_to_visualize.get("edges").append({'from': child_node, 'to': parent_node,
                                                        'label': edge})
            else:
                continue


def get_graph_to_visualize():
    get_all_classes(knowledge_graph)
    get_class_restrictions2(knowledge_graph)
    return graph_to_visualize


# get_graph_to_visualize()
