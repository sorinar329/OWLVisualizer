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
        self.chosen_class = None
        self.name2triples = {}
        self.restriction_idx = 0

    def set_triple(self, triple):
        if len(self.name2triples) == 0:
            self.chosen_class = triple[0]
        if triple[2].startswith("Res"):
            triple_name = f'Restriction{self.restriction_idx}'
            self.restriction_idx += 1
            triples = [triple]
            filtered_edges = []
            self.get_restriction(triple[2], filtered_edges)
            for edge in filtered_edges:
                triples.append([edge['from'], edge['label'], edge['to']])

            self.name2triples.update({triple_name: triples})
        else:
            if self.name2triples.get("Hierarchy") is None:
                self.name2triples.update({"Hierarchy": [triple]})
            else:
                triples = self.name2triples.pop("Hierarchy")
                triples.append(triple)
                self.name2triples.update({'Hierarchy': triples})

    def clear_triples(self):
        self.chosen_class = None
        self.name2triples = {}
        self.restriction_idx = 0

    def suggest_hierarchy(self):
        edges = self.kg_instance.get_graph_to_visualize().get("edges")

        filtered_hierarchy = []

        if self.name2triples.get("Hierarchy") is None:
            chosen_class = self.chosen_class
            hierarchy_triples = [[edge['from'], edge['label'], edge['to']] for edge in edges if
                                 edge['from'] == chosen_class and not edge['to'].startswith("Res")]
            filtered_hierarchy.extend(hierarchy_triples)
            return filtered_hierarchy

        else:
            hierarchy_triples = self.name2triples.get("Hierarchy")
            hierarchy_triples2 = [[edge['from'], edge['label'], edge['to']] for edge in edges if
                                  not edge['from'].startswith("Res")
                                  and not edge['to'].startswith("Res")]

            for triple in hierarchy_triples:
                for triple2 in hierarchy_triples2:
                    if triple[0] != triple2[0] and triple[2] == triple2[2]:
                        filtered_hierarchy.append(triple2)
                    if triple[2] == triple2[0]:
                        filtered_hierarchy.append(triple2)
                    if triple[0] != triple2[0] and triple[0] == triple2[2]:
                        filtered_hierarchy.append(triple2)

            filtered_hierarchy = [triple for triple in filtered_hierarchy if triple not in hierarchy_triples]
            filtered_hierarchy = list(set(tuple(triple) for triple in filtered_hierarchy))
            return filtered_hierarchy

    def suggest_restrictions(self):
        triples = []
        chosen_class = self.chosen_class
        edges = self.kg_instance.get_graph_to_visualize().get("edges")
        restriction_triples = [[edge['from'], edge['label'], edge['to']] for edge in edges if
                               edge['from'] == chosen_class and edge['to'].startswith("Res")]

        for r in range(self.restriction_idx):
            name = f'Restriction{r}'
            first_triple = self.name2triples.get(name)[0]
            restriction_triples.remove(first_triple)

        triples.extend(restriction_triples)
        return triples

    def has_suggestions(self):
        return len(self.mock_suggestion2()) > 0

    def mock_suggestion2(self):
        edges = self.kg_instance.get_graph_to_visualize().get("edges")
        suggest_triples = []
        whirlstorm_diving = "http://www.ease-crc.org/ont/mixing#WhirlstormThenCircularDivingToInner"
        triple = [edge for edge in edges if edge['from'] == whirlstorm_diving and edge['label'] == "subClassOf"][0]
        triple2 = [edge for edge in edges if edge['from'] == whirlstorm_diving and edge['label'] == "equivalentClass"][0]
        as_list = [triple['from'], triple['label'], triple['to']]
        as_list2 = [triple2['from'], triple2['label'], triple2['to']]
        #self.set_triple(as_list)
        #self.set_triple(as_list2)
        #self.set_triple(['http://www.ease-crc.org/ont/mixing#CompoundMotion', 'subClassOf', 'http://www.ease-crc.org/ont/mixing#Motion'])
        #self.set_triple(['http://www.ease-crc.org/ont/mixing#MixingMotion', 'subClassOf', 'http://www.ease-crc.org/ont/mixing#Motion'])

        if len(self.name2triples) == 0:
            for edge in edges:
                if edge['from'].startswith("Res"):
                    continue
                suggest_triples.extend([[edge['from'], edge['label'], edge['to']]])

        else:
            suggest_triples.extend(self.suggest_restrictions())
            suggest_triples.extend(self.suggest_hierarchy())
            print(list(self.name2triples.keys()))

        mocked_solution = {'subjects': []}
        for triple in suggest_triples:
            s = [subject for subject in mocked_solution['subjects'] if subject['iri'] == str(triple[0])]
            if len(s) == 0:
                subject = {'iri': str(triple[0]),
                           'label': graph_utility.uri_or_literal_2label(self.kg, triple[0]),
                           'type': 'Classes', 'predicates': []}
                mocked_solution['subjects'].append(subject)
                s = subject
            else:
                s = s[0]

            p = [predicate for predicate in s['predicates'] if predicate['iri'] == str(triple[1])]

            if len(p) == 0:
                predicate = {'iri': str(triple[1]),
                             'label': triple[1],
                             'type': 'Relations', 'objects': []}
                s['predicates'].append(predicate)
                p = predicate
            else:
                p = p[0]
            obj = {'iri': str(triple[2]), 'label': graph_utility.uri_or_literal_2label(self.kg, triple[2]),
                   'type': 'Classes'}
            p['objects'].append(obj)
        return mocked_solution

    def get_partial_viz_graph(self):
        triples = self.get_latest_triples()
        graph_viz = self.kg_instance.get_graph_to_visualize()
        graph_nodes = graph_viz.get("nodes")
        graph_edges = graph_viz.get("edges")
        filtered_graph = {'nodes': [], 'edges': []}
        nodes = set()
        filtered_edges = []
        for triple in triples:
            for edge in graph_edges:
                if triple[0] == edge['from'] and triple[1] == edge['label'] and triple[2] == edge['to']:
                    nodes.add(triple[0])
                    nodes.add(triple[2])
                    if edge['label'] == ' ':
                        edge['label'] = ''
                    filtered_edges.append(edge)

        filtered_nodes = [node for node in graph_nodes if node['id'] in nodes]
        filtered_graph.get('nodes').extend(filtered_nodes)
        filtered_graph.get('edges').extend(filtered_edges)

        return filtered_graph

    def get_restriction(self, subject, filtered_graph):
        graph_viz = self.kg_instance.get_graph_to_visualize()
        filtered_edges = [edge for edge in graph_viz.get("edges") if edge['from'] == subject]

        for edge in filtered_edges:
            o = edge['to']
            filtered_graph.append(edge)
            self.get_restriction(o, filtered_graph)

    def get_latest_triples(self):
        name = list(self.name2triples.keys())[-1]
        latest_triple = self.name2triples.get(name)
        return latest_triple


def get_query_builder(kg_instance):
    return QueryBuilder(kg_instance)


qb = get_query_builder(kg_instance=graph.KnowledgeGraph('data/mixing.owl'))
#qb.mock_suggestion2()
#print(qb.get_partial_viz_graph())

