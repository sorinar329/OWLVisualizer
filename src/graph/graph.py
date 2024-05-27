import rdflib
from rdflib import OWL, RDFS, RDF
from rdflib.term import BNode, URIRef, Literal

from src.graph.graph_utility import recursive_pattern_matching, extract_property_value, uri_or_literal_2label, \
    extract_cardinality_types
from src.graph.types import get_cardinality_name, get_collection_name, is_restriction, \
    is_cardinality, is_collection, get_restriction_name
import src.graph.coloring as coloring

import random


class KnowledgeGraph:
    def __init__(self, knowledge_graph_file: str):
        self.kg = rdflib.Graph().parse(knowledge_graph_file)
        self.graph_to_visualize = {'nodes': [], 'edges': []}
        self.dominant_namespace = ''

        self._set_dominant_namespace()
        self._add_class_hierarchy()
        self._add_class_restrictions()
        self._color_graph()

    def _add_node(self, node_id: str, label: str = ""):
        if label == "":
            label = uri_or_literal_2label(self.kg, node_id)
        self.graph_to_visualize.get("nodes").append(
            {'id': node_id, 'label': label})

    def _add_edge(self, source_id: str, target_id: str, edge_label: str):
        self.graph_to_visualize.get("edges").append(
            {'from': source_id, 'to': target_id, 'label': edge_label,
             'arrows': 'to'})

    def _add_class_hierarchy(self):
        nodes = set()
        for subclass, superclass in self.kg.subject_objects(RDFS.subClassOf):
            if isinstance(superclass, BNode):
                continue

            nodes.add(subclass)
            nodes.add(subclass)
            self._add_edge(source_id=str(subclass), target_id=str(superclass), edge_label='subClassOf')
        for node in nodes:
            self._add_node(node_id=str(node))

    def _add_class_restrictions(self):
        classes_with_restrictions = [[s, p, o] for (s, p, o)
                                     in self.kg.triples(
                (None, RDFS.subClassOf, None))
                                     if isinstance(o, BNode)]
        classes_with_restrictions.extend([[s, p, o] for (s, p, o)
                                          in self.kg.triples((None, OWL.equivalentClass, None))
                                          if isinstance(o, BNode)])
        for s, p, o in classes_with_restrictions:
            self._handle_bnode(parent_node=o, parent_id=str(s), edge_label=uri_or_literal_2label(self.kg, p))

    def _list_recursion(self, parent_node, parent_id, edge_label):

        for triple in self.kg.triples((parent_node, None, None)):
            if triple[1] == RDF.first:
                if isinstance(triple[2], BNode):
                    self._handle_bnode(parent_node=triple[2], parent_id=parent_id, edge_label=edge_label)
                else:
                    edge_label, child_node = '', f'Res-{random.randint(0, 1000000000000)}#{triple[2]}'
                    self._add_node(node_id=child_node)
                    self._add_edge(source_id=str(parent_id), target_id=child_node, edge_label=edge_label)
            else:
                self._list_recursion(parent_node=triple[2], parent_id=parent_id, edge_label=edge_label)

    def _handle_bnode(self, parent_node, parent_id, edge_label):
        child_id = ''
        child_node = None
        child_label = ''
        for s, p, o in self.kg.triples((parent_node, None, None)):
            assert isinstance(p, URIRef)
            if p == OWL.complementOf:
                edge_label += ' not'
                child_id = f'Res-{random.randint(0, 1000000000000)}#{o}'

            elif is_restriction(p):
                edge_label += f' {get_restriction_name(p)}'
                if isinstance(o, BNode):
                    self._handle_bnode(parent_node=o, parent_id=parent_id, edge_label=edge_label)
                else:
                    child_id = f'Res-{random.randint(0, 1000000000000)}#{o}'
            elif is_cardinality(p):
                edge_label += f' {get_cardinality_name(p)} {o}'

            elif is_collection(p):
                child_id = (f'Res-{random.randint(0, 1000000000000)}#'
                            f'{get_collection_name(p)}-{random.randint(0, 100000)}')
                child_node = o
                child_label = get_collection_name(p)

            elif p == OWL.onClass:
                child_id = f'Res-{random.randint(0, 1000000000000)}#{o}'

            if p == OWL.onProperty:
                edge_label += f'/{uri_or_literal_2label(self.kg, o)}'

        if child_id != '':
            self._add_node(child_id, child_label)
            if len(edge_label) > 1 and edge_label[0] == '/':
                edge_label = edge_label[1:]
            self._add_edge(source_id=parent_id, target_id=child_id, edge_label=edge_label)

            if isinstance(child_node, BNode):
                self._list_recursion(parent_node=child_node, parent_id=child_id, edge_label='')

    def get_graph_to_visualize(self):
        return self.graph_to_visualize

    def get_rdflib_graph(self):
        return self.kg

    def _color_graph(self):
        coloring.color_classes(self.graph_to_visualize)
        coloring.color_parameters(self.graph_to_visualize)
        coloring.color_edges(self.graph_to_visualize)
        coloring.color_tasks_actions(self.kg, self.graph_to_visualize)
        coloring.color_dispositions(self.kg, self.graph_to_visualize)
        coloring.color_tools(self.kg, self.graph_to_visualize)
        coloring.color_instances(self.graph_to_visualize)

    def _set_dominant_namespace(self):
        iris = []
        for s, p, o in self.kg.triples((None, RDFS.subClassOf, None)):
            if isinstance(s, BNode) or isinstance(o, BNode):
                continue
            subject_iri, object_iri = str(s), str(o)
            if '#' in subject_iri:
                base_iri = subject_iri.split('#')[0] + '#'
                iris.append(base_iri)
            else:
                last_slash_index = subject_iri.rfind('/')
                base_iri = subject_iri[:last_slash_index] + '/'
                iris.append(base_iri)
            if '#' in object_iri:
                base_iri = object_iri.split('#')[0] + '#'
                iris.append(base_iri)
            else:
                last_slash_index = object_iri.rfind('/')
                base_iri = object_iri[:last_slash_index] + '/'
                iris.append(base_iri)

        count = {}
        for iri in iris:
            if iri in count:
                count[iri] += 1
            else:
                count[iri] = 1

        self.dominant_namespace = max(count, key=lambda key: count[key])
