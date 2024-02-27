from rdflib import Graph, URIRef, RDF, OWL
import rdflib.util

from collections import defaultdict
import json

motion = "http://www.ease-crc.org/ont/mixing#WhirlstormMotion"
knowledge_graph = Graph()
knowledge_graph.parse("data/mixing.owl")


class QueryBuilder:
    def __init__(self, knowledge_graph: rdflib.Graph):
        self.kg = knowledge_graph
        self.triples = []
        self.sparql_query = "SELECT * WHERE { "

    def add_triple(self, triple: ()):
        self.triples.append(triple)

    def suggest_triples(self, triple: ()):
        if triple[0] is None:
            return self.kg.triples(triple)
        elif triple[0] is not None:
            return self.kg.predicate_objects(triple[0])

        for s, p, o in self.kg.triples(triple):
            print(s, p, o)

    def mock_suggestion(self):
        suggestions = list(self.kg.triples((URIRef(motion), None, None)))
        mocked_solution = []
        for s, p, o in suggestions:
            mocked_solution.append([str(s), str(p), str(o)])
        return mocked_solution
        # for s, p, o in self.kg.triples((URIRef(motion), None, None)):
        #     print(s, p, o)
        # for s2, p2, o2 in self.kg.triples((o, OWL.intersectionOf, None)):
        #     print(p2, o2)
        #     for s3, p3, o3 in self.kg.triples((o2, RDF.first, None)):
        #         print(s3, p3, o3)
        #         for s4, p4, o4 in self.kg.triples((o3, None, None)):
        #             print(s4, p4, o4)

    def mock_suggestion2(self):
        suggestions = list(self.kg.triples((URIRef(motion), None, None)))
        mocked_solution = {}
        for triple in suggestions:
            s, p, o = [str(s) for s in triple]
            # Erstelle das Subjekt, falls es noch nicht existiert
            if s not in mocked_solution:
                mocked_solution[s] = {}

            if p not in mocked_solution[s]:
                mocked_solution[s][p] = []

            mocked_solution[s][p].append(o)
        return mocked_solution


def get_query_builder():
    return QueryBuilder(knowledge_graph)
