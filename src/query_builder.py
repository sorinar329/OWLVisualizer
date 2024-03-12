from rdflib import Graph, URIRef, RDF, OWL, BNode, RDFS
import rdflib.util

from collections import defaultdict
import json

from graph import graph_utility

motion = "http://www.ease-crc.org/ont/mixing#WhirlstormMotion"
motion2 = "http://www.ease-crc.org/ont/mixing#CircularMotion"
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

    def set_triple(self, triple):
        self.triples.append(triple)

    def mock_suggestion2(self):
        suggest_triples = []
        if len(self.triples) == 0:

            classes = list(self.kg.subject_objects(RDFS.subClassOf))
            individuals = list(self.kg.subjects(RDF.type, OWL.NamedIndividual))
            for cls, _ in classes:
                suggest_triples.extend(list(self.kg.triples((cls, None, None))))
            for individual in individuals:
                suggest_triples.extend(list(self.kg.triples((individual, None, None))))

        else:
            suggest_triples = list(self.kg.triples((URIRef(self.triples[-1][2]), None, None)))
        suggest_triples = [(sub, pred, obj) for sub, pred, obj in suggest_triples if not isinstance(sub, BNode)]
        suggest_triples = [(sub, pred, obj) for sub, pred, obj in suggest_triples if obj != OWL.NamedIndividual]
        suggest_triples = [(sub, pred, obj) for sub, pred, obj in suggest_triples if obj != OWL.Class]
        mocked_solution = {'subjects': []}
        for triple in suggest_triples:
            s = [subject for subject in mocked_solution['subjects'] if subject['iri'] == str(triple[0])]
            if len(s) == 0:
                if list(self.kg.objects(triple[0], RDF.type))[0] == OWL.NamedIndividual:
                    type_s = 'Instances'
                elif list(self.kg.objects(triple[0], RDF.type))[0] == OWL.Class:
                    type_s = 'Classes'
                elif list(self.kg.objects(triple[0], RDF.type))[0] == OWL.Restriction:
                    type_s = 'Restrictions'
                else:
                    type_s = 'Other'

                subject = {'iri': str(triple[0]), 'label': graph_utility.uri_or_literal_2label(triple[0]),
                           'type': type_s, 'predicates': []}
                mocked_solution['subjects'].append(subject)
                s = subject
            else:
                s = s[0]
            pred, obj = triple[1], triple[2]
            # if isinstance(obj, BNode) and graph_utility.is_restriction(self.kg, obj):
            #     pred, obj = graph_utility.extract_restriction(self.kg, obj)
            #     print(pred, obj)

            p = [predicate for predicate in s['predicates'] if predicate['iri'] == str(triple[1])]

            if len(p) == 0:
                if pred == RDFS.label:
                    type_p = 'Labels'
                elif pred == OWL.equivalentClass:
                    type_p = 'Equivalent To'
                elif pred == RDFS.subClassOf:
                    type_p = 'SubClassOf'
                elif pred == RDF.type:
                    type_p = 'Is a'
                elif list(self.kg.objects(pred, RDF.type))[0] == OWL.DatatypeProperty:
                    type_p = 'Attributes'
                elif list(self.kg.objects(pred, RDF.type))[0] == OWL.ObjectProperty:
                    type_p = 'Relations'
                else:
                    type_p = 'Other'
                predicate = {'iri': str(triple[1]), 'label': graph_utility.uri_or_literal_2label(triple[1]),
                             'type': type_p, 'objects': []}
                s['predicates'].append(predicate)
                p = predicate
            else:
                p = p[0]
            obj = {'iri': str(triple[2]), 'label': graph_utility.uri_or_literal_2label(triple[2]), 'type': 'Classes'}
            p['objects'].append(obj)
        return mocked_solution

    def mock_suggestions3(self):
        suggestions = list(self.kg.triples((URIRef(motion), None, None)))
        mocked_solution = {}
        for s, p, o in suggestions:

            s_label = graph_utility.uri_or_literal_2label(node=s)
            p_label = graph_utility.uri_or_literal_2label(node=p)
            o_label = graph_utility.uri_or_literal_2label(node=o)

            if s not in mocked_solution:
                mocked_solution[s] = {s_label: {}}
                if isinstance(s, BNode) and graph_utility.is_list(self.kg, bnode=s):
                    print(f'Subject: {s}')

            if isinstance(o, BNode):
                for _, p2, o2 in self.kg.triples((o, None, None)):
                    t = graph_utility.get_collection_type(p2)
                    # mocked_solution[s][s_label][str(p2)][t[1]].append([o2, t[0]])
                # if graph_utility.is_list(self.kg, o):
                #     print(f'Object: {o}')
                #     for t2 in self.kg.triples((o, None, None)):
                #         for _, p2, o2 in self.kg.triples((t2[2], None, None)):
                #             print(p2, o2)
                #
                #             print(graph_utility.extract_collection_recursive(self.kg, (None, p2, o2)))
            else:
                if p not in mocked_solution[s][s_label]:
                    mocked_solution[s][s_label][p] = {p_label: []}

                mocked_solution[s][s_label][p][p_label].append([o, o_label])

        return mocked_solution


def get_query_builder():
    return QueryBuilder(knowledge_graph)


friends = [{'iri': 'http://bla#Alice', 'label': 'Alice'}, {'iri': 'http://bla#Bob', 'label': 'Bob'}]
hasFriendsRelation = {'iri': 'hasFriendRelation', 'label': 'hasFriend', 'objects': friends}
anotherFriend = {'iri': 'http://bla#Charlie', 'label': 'Charlie', 'predicate': [hasFriendsRelation]}
suggestions = {'subject': [anotherFriend]}

# print(suggestions['subject'][0]['iri'])
#
# for s in suggestions['subject']:
#     print(s['iri'])
#     for p in s['predicate']:
#         print(p['iri'])
#         for o in p['objects']:
#             print(o['iri'])


suggest = get_query_builder().mock_suggestion2()
#
# for sub in suggest['subjects']:
#     print(f'Subject is:' + sub['iri'])
#     print(f'Subject is:' + sub['type'])
#     for p in sub['predicates']:
#         print(f'Predicate is' + p['iri'])
#         for obj in p['objects']:
#             print(f'Object is' + obj['iri'])
