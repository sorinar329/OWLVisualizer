import rdflib
from rdflib import OWL, RDFS, RDF
from rdflib.term import BNode, URIRef, Literal

from src.graph.graph_utility import recursive_pattern_matching, extract_property_value, uri_or_literal_2label, \
    extract_cardinality_types
from src.graph.types import get_cardinality_name, get_collection_name, is_restriction, \
    is_cardinality, is_collection, get_restriction_name
import random


class KnowledgeGraph:
    def __init__(self, knowledge_graph_file: str):
        self.kg = rdflib.Graph().parse(knowledge_graph_file)
        self.graph_to_visualize = {'nodes': [], 'edges': []}
        self._add_class_hierarchy()
        self._add_class_restrictions()

    def _add_node(self, node_id: str):
        label = uri_or_literal_2label(self.kg, node_id)
        self.graph_to_visualize.get("nodes").append(
            {'id': node_id, 'label': label})

    def _add_edge(self, parent_id: str, child_id: str, edge_label: str):
        self.graph_to_visualize.get("edges").append(
            {'from': child_id, 'to': parent_id, 'label': edge_label,
             'arrows': 'from'})

    def _add_class_hierarchy(self):
        nodes = set()
        for subclass, superclass in self.kg.subject_objects(RDFS.subClassOf):
            if isinstance(superclass, BNode):
                continue

            nodes.add(subclass)
            nodes.add(subclass)
            self._add_edge(parent_id=str(subclass), child_id=str(superclass), edge_label='subClassOf')
        for node in nodes:
            self._add_node(node_id=str(node))

    def _add_class_restrictions(self):
        classes_with_restrictions = [[s, p, o] for (s, p, o)
                                     in self.kg.triples((None, RDFS.subClassOf, None))
                                     if isinstance(o, BNode)]
        classes_with_restrictions.extend([[s, p, o] for (s, p, o)
                                          in self.kg.triples((None, OWL.equivalentClass, None))
                                          if isinstance(o, BNode)])
        grouped_triples = []

        for s, p, o in classes_with_restrictions:
            triples = [[s, p, o]]
            recursive_pattern_matching(self.kg, o, triples)

            grouped_triples.append(triples)
        collection_idx = 0

        for group in grouped_triples:
            parent_node, edge = '', ''
            for s, p, o in group:
                if p == RDFS.subClassOf or p == OWL.equivalentClass:
                    parent_node = str(s)
                    edge = uri_or_literal_2label(self.kg, p)
                elif is_restriction(p):
                    e, n = extract_property_value(self.kg, s)
                    if e is not None and n is not None:
                        child_node = f'Res-{random.randint(0, 1000000000000)}#{n}'
                        edge += f'/{uri_or_literal_2label(self.kg, e)} {get_restriction_name(p)}'
                        if edge[0] == '/':
                            edge = edge[1:]
                        self._add_node(node_id=child_node)
                        self._add_edge(parent_id=parent_node, child_id=child_node, edge_label=edge)
                        edge = ''
                    else:
                        edge += f'/{uri_or_literal_2label(self.kg, e)} '
                        edge += f'{uri_or_literal_2label(self.kg, get_restriction_name(p))}'
                elif is_cardinality(p):
                    cardinality_property, cardinality, cls = extract_cardinality_types(self.kg, s)
                    edge += f'{get_cardinality_name(cardinality_property)} {cardinality}'
                    if edge[0] == '/':
                        edge = edge[1:]
                    child_node = f'Res-{random.randint(0, 1000000000000)}#{cls}'
                    self._add_node(node_id=child_node)
                    self._add_edge(parent_id=parent_node, child_id=child_node, edge_label=edge)
                    edge = ''
                elif is_collection(p):
                    name = get_collection_name(p)
                    child_node = f'Res#{name}-{collection_idx}'
                    self._add_node(node_id=child_node)
                    self._add_edge(parent_id=parent_node, child_id=child_node, edge_label=edge)
                    collection_idx += 1
                    parent_node = child_node
                    edge = ''
                elif p == RDF.first and isinstance(o, URIRef) or isinstance(o, Literal):
                    edge, child_node = '', o
                    child_node = f'Res-{random.randint(0, 1000000000000)}#{child_node}'
                    self._add_node(node_id=child_node)
                    self._add_edge(parent_id=str(parent_node), child_id=child_node, edge_label=edge)
                else:
                    continue

    def get_graph_to_visualize(self):
        return self.graph_to_visualize

    def get_rdflib_graph(self):
        return self.kg

# def get_instances(kg: Graph):
#     nodes = set()
#     for instance, _, cls in kg.triples((None, RDF.type, OWL.NamedIndividual)):
#         nodes.add(instance)
#
#     for node in nodes:
#         for _, _, o in kg.triples((node, RDF.type, None)):
#             if o == OWL.NamedIndividual or URIRef('http://www.w3.org/2003/11/swrl#Imp'):
#                 continue
#             graph_to_visualize.get("edges").append({'from': str(node), 'to': str(o), 'label': 'is a'})
#             graph_to_visualize.get("nodes").append({'id': str(node), 'label': uri_or_literal_2label(kg, node),
#                                                     'shape': 'box'})

# kg = KnowledgeGraph('data/food_cutting.owl')
