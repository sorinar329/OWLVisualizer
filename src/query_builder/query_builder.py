from rdflib import Graph, URIRef, RDF, OWL, BNode, RDFS
import rdflib.util
import src.graph.graph as graph
from src.graph.graph_utility import extract_property_value

from src.graph import graph_utility

motion = "http://www.ease-crc.org/ont/mixing#CircularDivingToInnerMotion"
motion2 = "http://www.ease-crc.org/ont/mixing#CircularMotion"


class QueryBuilder:
    def __init__(self, knowledge_graph: graph.KnowledgeGraph):
        self.kg_instance = knowledge_graph
        self.kg = knowledge_graph.get_rdflib_graph()
        self.triples = []

    def set_triple(self, triple):
        self.triples.append(triple)

    def clear_triples(self, clear_triples: list = None):
        if clear_triples is []:
            self.triples = []
        else:
            for triple in clear_triples:
                self.triples.remove(triple)

    def get_filtered_graph(self):
        filtered_graph = {'nodes': [], 'edges': []}
        nodes = set()
        original_nodes = self.kg_instance.get_graph_to_visualize().get("nodes")
        original_edges = self.kg_instance.get_graph_to_visualize().get("edges")
        for triple in self.triples:
            nodes.add(triple[0])
            nodes.add(triple[2])
            edge_label = triple[1]
            if edge_label == ' ':
                edge_label = ''
            edge = [edge for edge in original_edges if triple[0] == edge['from'] and edge_label == edge['label']
                    and triple[2] == edge['to']][0]
            filtered_graph.get('edges').append(edge)

        filtered_nodes = [node for node in original_nodes if node['id'] in nodes]
        filtered_graph.get('nodes').extend(filtered_nodes)
        return filtered_graph

    def get_typeof_node(self, node: URIRef):
        node_type = {OWL.Class: 'Classes', RDF.type: 'Is a', OWL.DatatypeProperty: 'Attributes',
                     OWL.ObjectProperty: 'Relations', OWL.equivalentClass: 'Relations', RDFS.subClassOf: 'Relations',
                     RDFS.label: 'Labels', OWL.NamedIndividual: 'Instances'}

        if node in node_type:
            return node_type[node]
        else:
            for o in self.kg.objects(node, RDF.type):
                if node_type[o] is not None:
                    return node_type[o]
                else:
                    return 'Other'

    def get_typeof_predicate(self, predicate: str):
        try:
            node_type = {'subClassOf': 'Relations'}
            return node_type[predicate]

        except:
            return 'Other'

    def get_hierarchical_triples(self):
        triples = []
        taxonomy_triples = [triple for triple in self.triples if
                            triple[1] == 'subClassOf' or triple[1] == 'equivalentTo']
        edges = [edge for edge in self.kg_instance.get_graph_to_visualize().get("edges") if
                 (edge['label'] == 'subClassOf' or edge['label'] == 'equivalentTo')]
        edges.extend([edge for edge in self.kg_instance.get_graph_to_visualize().get("edges") if
                      edge['from'] == self.triples[0][0]])

        for edge in edges:
            set1 = {element for s, p, o in taxonomy_triples for element in (s, o)}
            set2 = {edge['from'], edge['to']}
            intersecting_triples = set2.intersection(set1)
            if len(intersecting_triples) == 1:
                triples.append([edge['from'], edge['label'], edge['to']])

        return triples

    def get_restriction_triples(self):
        triples = []
        restriction_triples = [triple for triple in self.triples if
                               (triple[0].startswith('Res') or triple[2].startswith('Res'))]
        edges = [edge for edge in self.kg_instance.get_graph_to_visualize().get("edges") if
                 (edge['from'].startswith('Res') and edge['to'].startswith('Res'))]
        edges.extend([edge for edge in self.kg_instance.get_graph_to_visualize().get("edges") if
                      edge['from'] == self.triples[0][0]])

        for edge in edges:
            set1 = {element for s, p, o in restriction_triples for element in (s, o)}
            set2 = {edge['from'], edge['to']}
            intersecting_triples = set2.intersection(set1)
            if len(intersecting_triples) == 1:
                edge_label = edge['label']
                if edge_label == '':
                    edge_label = ' '
                triples.append([edge['from'], edge_label, edge['to']])

        # print(f"These are my triples: {triples}")
        return triples

    def mock_suggestion2(self):
        edges = self.kg_instance.get_graph_to_visualize().get("edges")
        suggest_triples = []
        if len(self.triples) == 0:
            for edge in edges:
                if edge['from'].startswith("Res"):
                    continue
                suggest_triples.extend([[edge['from'], edge['label'], edge['to']]])

        else:
            suggest_triples.extend(self.get_restriction_triples())
            suggest_triples.extend(self.get_hierarchical_triples())

        mocked_solution = {'subjects': []}
        for triple in suggest_triples:
            type_triple = ''

            if (triple[1] == RDFS.subClassOf or triple[1] == OWL.equivalentClass) and not triple[2].startswith('Res'):
                type_triple = 'Hierarchy'
            elif triple[0].startswith('Res') or triple[2].startswith('Res'):
                type_triple = 'Restriction'

            s = [subject for subject in mocked_solution['subjects'] if subject['iri'] == str(triple[0])]
            if len(s) == 0:
                # type_subject = self.get_typeof_node(URIRef(triple[0]))
                subject = {'iri': str(triple[0]),
                           'label': graph_utility.uri_or_literal_2label(self.kg, triple[0]),
                           'type': 'Classes', 'predicates': []}
                mocked_solution['subjects'].append(subject)
                s = subject
            else:
                s = s[0]

            p = [predicate for predicate in s['predicates'] if predicate['iri'] == str(triple[1])]

            if len(p) == 0:
                type_predicate = self.get_typeof_predicate(triple[1])

                predicate = {'iri': str(triple[1]),
                             'label': triple[1],
                             'type': 'Relations', 'objects': []}
                s['predicates'].append(predicate)
                p = predicate
            else:
                p = p[0]
            # type_object = self.get_typeof_node(URIRef(triple[2]))
            obj = {'iri': str(triple[2]), 'label': graph_utility.uri_or_literal_2label(self.kg, triple[2]),
                   'type': 'Classes'}
            p['objects'].append(obj)
        return mocked_solution


def get_query_builder(kg_instance):
    return QueryBuilder(kg_instance)

# qb = get_query_builder(kg_instance=graph.KnowledgeGraph('data/food_cutting.owl'))
# qb.mock_suggestion2()
