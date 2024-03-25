from rdflib import Graph, OWL, RDFS, RDF
from rdflib.term import BNode, URIRef, Literal
from src.graph.graph_utility import recursive_pattern_matching, extract_property_value, uri_or_literal_2label
import random

knowledge_graph = Graph()
knowledge_graph.parse("data/mixing.owl")

graph_to_visualize = {'nodes': [], 'edges': []}

restriction_type = [OWL.hasValue, OWL.someValuesFrom, OWL.allValuesFrom]
collection_type = {OWL.intersectionOf: ('Intersection', 'owl:intersectionOf'), OWL.unionOf: ('Union', 'owl:unionOf')}


def get_all_classes(kg: Graph):
    nodes = set()
    for subclass, superclass in kg.subject_objects(RDFS.subClassOf):
        if isinstance(superclass, BNode):
            continue
        nodes.add(subclass)
        nodes.add(subclass)
        graph_to_visualize.get("edges").append({'from': str(subclass), 'to': str(superclass), 'label': 'subClassOf'})
    for node in nodes:
        graph_to_visualize.get("nodes").append({'id': str(node), 'label': uri_or_literal_2label(node)})


def get_class_restrictions2(knowledge_graph):
    classes_with_restrictions = [[cls, res] for (cls, res)
                                 in knowledge_graph.subject_objects(RDFS.subClassOf)
                                 if isinstance(res, BNode)]
    grouped_triples = []

    for cls, restrictions in classes_with_restrictions:
        triples = [[cls, RDFS.subClassOf, restrictions]]
        recursive_pattern_matching(knowledge_graph, restrictions, triples)

        grouped_triples.append(triples)
    collection_idx = 0

    for group in grouped_triples:
        parent_node, edge, child_node = '', '', ''
        for s, p, o in group:
            if p == RDFS.subClassOf:
                parent_node = str(s)
                edge = uri_or_literal_2label(p)
            elif p in restriction_type:
                e, n = extract_property_value(knowledge_graph, s)
                if e is not None and n is not None:
                    child_node = n
                    child_label = uri_or_literal_2label(child_node)
                    edge += f'/{uri_or_literal_2label(e)}'
                    if edge[0] == '/':
                        edge = edge[1:]
                    child_node = f'{child_node}_{random.randint(0, 1000000000000)}'
                    graph_to_visualize.get("nodes").append({'id': child_node, 'label': child_label})
                    graph_to_visualize.get("edges").append({'from': child_node, 'to': parent_node,
                                                            'label': edge})
                    edge = ''
                else:
                    edge += f'/{uri_or_literal_2label(e)}'
                    edge += f'/{uri_or_literal_2label(p)}'

            elif p in collection_type:
                name, _ = collection_type.get(p)
                child_node = f'{name}-{collection_idx}'
                collection_idx += 1
                edge += f'/{uri_or_literal_2label(p)}'
                graph_to_visualize.get("nodes").append({'id': child_node, 'label': child_node})
                graph_to_visualize.get("edges").append({'from': child_node, 'to': parent_node,
                                                        'label': edge})
                parent_node = child_node
                edge = ''
            elif p == RDF.first and isinstance(o, URIRef) or isinstance(o, Literal):
                edge, child_node = '', o
                child_label = uri_or_literal_2label(child_node)
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


def get_classes():
    return get_all_classes(knowledge_graph)

# get_graph_to_visualize()
