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
        self.latest_triple = None

    def set_triple(self, triple):
        if triple[2].startswith("Res"):
            self.latest_triple = triple
            self.triples.append(triple)
            filtered_edges = []
            self.get_restriction(triple[2], filtered_edges)
            for edge in filtered_edges:
                self.triples.append([edge['from'], edge['label'], edge['to']])
        else:
            self.latest_triple = triple
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
        edges = self.kg_instance.get_graph_to_visualize().get("edges")

        filtered_hierarchy = []

        self.get_hierarchy(filtered_hierarchy)
        for edge in filtered_hierarchy:
            for edge2 in edges:
                if edge['from'] == edge2['to'] or edge['to'] == edge2['from']:
                    triples.append([edge2['from'], edge2['label'], edge2['to']])
        triples = [triple for triple in triples if triple not in self.triples]
        return triples

    def get_restriction_triples(self):
        triples = []
        chosen_class = self.triples[0][0]
        edges = self.kg_instance.get_graph_to_visualize().get("edges")
        restriction_triples = [edge for edge in edges if
                               edge['from'] == chosen_class and edge['to'].startswith('Res')]

        for s, p, o in self.triples:
            for edge in restriction_triples:
                if o == edge['to']:
                    restriction_triples.remove(edge)
        for edge in restriction_triples:
            triples.append([edge['from'], edge['label'], edge['to']])
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

    def get_partial_viz_graph(self, triple):
        filtered_edges = []
        s, p, o = triple
        graph_viz = self.kg_instance.get_graph_to_visualize()

        edge = [edge for edge in graph_viz.get("edges") if
                edge['from'] == s and edge['label'] == p
                and edge['to'] == o][0]
        o = edge.get('to')
        if o.startswith('Res'):
            filtered_edges.append(edge)
            self.get_restriction(o, filtered_edges)
            for edge in filtered_edges:
                print(edge['from'], edge['label'], edge['to'])
        else:
            self.get_hierarchy(filtered_edges)
        filtered_graph = {'nodes': [], 'edges': []}
        nodes = set()
        original_nodes = self.kg_instance.get_graph_to_visualize().get("nodes")
        original_edges = self.kg_instance.get_graph_to_visualize().get("edges")
        for edge in filtered_edges:
            nodes.add(edge['from'])
            nodes.add(edge['to'])
            edge_label = edge['label']
            if edge_label == ' ':
                edge_label = ''

            edge = [e for e in original_edges if e['from'] == edge['from'] and edge_label == edge['label']
                    and e['to'] == edge['to']][0]
            filtered_graph.get('edges').append(edge)
        filtered_nodes = [node for node in original_nodes if node['id'] in nodes]
        filtered_graph.get('nodes').extend(filtered_nodes)
        self.latest_triple = None
        return filtered_graph

    def get_restriction(self, subject, filtered_graph):
        graph_viz = self.kg_instance.get_graph_to_visualize()
        filtered_edges = [edge for edge in graph_viz.get("edges") if edge['from'] == subject]

        for edge in filtered_edges:
            o = edge['to']
            filtered_graph.append(edge)
            self.get_restriction(o, filtered_graph)

    def restriction_to_owl_expression(self):
        triples = [['http://www.ease-crc.org/ont/SOMA.owl#Dicing', 'subClassOf', 'Res-60539982743#AND-50310'],
                   ['Res-60539982743#AND-50310', 'hasInputObject some',
                    'Res-950690259655#http://www.ease-crc.org/ont/food_cutting#Stripe'],
                   [
                       'Res-60539982743#AND-50310', 'hasResultObject exactly 1',
                       'Res-319911140559#http://www.ease-crc.org/ont/food_cutting#Cube'],
                   [
                       'Res-60539982743#AND-50310', 'hasResultObject exactly 1',
                       'Res-150494678859#http://www.ease-crc.org/ont/food_cutting#Stripe#']]

        graph_viz = self.kg_instance.get_graph_to_visualize()
        nodes = graph_viz.get("nodes")
        owl_expression = ""
        for s, p, o in triples:
            if not s.startswith("Res"):
                subject = s
                node = [node for node in nodes if node['id'] == s]
                if len(node) == 1:
                    subject = node[0].get('label')

                owl_expression += f'{subject} {p} '
            else:
                obj = o
                node = [node for node in nodes if node['id'] == o]
                if len(node) == 1:
                    obj = node[0].get('label')
                owl_expression += f'({p} {obj}) AND '
        print(owl_expression)

    def get_hierarchy(self, filtered_graph):
        graph_viz = self.kg_instance.get_graph_to_visualize()
        triples_without_res = [(s, p, o) for s, p, o in self.triples if
                               not s.startswith('Res') or not o.startswith('Res')]
        for s, p, o in triples_without_res:
            for edge in graph_viz.get('edges'):
                if edge['from'] in s and edge['label'] in p and edge['to'] in o:
                    filtered_graph.append(edge)

    def get_latest_triple(self):
        return self.latest_triple


def get_query_builder(kg_instance):
    return QueryBuilder(kg_instance)


qb = get_query_builder(kg_instance=graph.KnowledgeGraph('data/food_cutting.owl'))
# qb.restriction_to_owl_expression()
# qb.set_triple(['http://www.ease-crc.org/ont/SOMA.owl#Dicing', 'subClassOf',
#               'http://www.ease-crc.org/ont/food_cutting#CuttingAction'])
# qb.mock_suggestion2()
# qb.set_triple(triple=['http://purl.obolibrary.org/obo/PO_0030102', 'subClassOf',
#                       ' http://purl.obolibrary.org/obo/FOODON_00001057'])
# qb.get_partial_viz_graph(triple=['http://purl.obolibrary.org/obo/FOODON_00003523', 'subClassOf',
#                                  'http://purl.obolibrary.org/obo/PO_0030102'])
