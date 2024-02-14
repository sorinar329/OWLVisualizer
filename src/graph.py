import rdflib
from rdflib import Graph, OWL, RDFS, RDF
from rdflib.term import BNode

knowledge_graph = Graph()
knowledge_graph.parse("/home/mkuempel/Downloads/mixing.owl")


# for o, s in knowledge_graph.subject_objects(RDFS.subClassOf):
#   print(type(s))
# for _, _, intersection in knowledge_graph.triples((s, OWL.intersectionOf, None)):
#     for _,_,first in knowledge_graph.triples((intersection, RDF.first, None)):
#         for property, value in knowledge_graph.predicate_objects(first):
#             print(property, value)
#
#     for _,_,rest in knowledge_graph.triples((intersection, RDF.rest, None)):
#         for _,_,first in knowledge_graph.triples((rest, RDF.first, None)):
#             for property, value in knowledge_graph.predicate_objects(first):
#                 print(property, value)
# for _,_, property in knowledge_graph.triples((first, OWL.onProperty, None)):
#      print(property)
# for _,_, value in knowledge_graph.triples((first, OWL.hasValue, None)):
#      print(value)


def get_all_classes(kg: Graph):
    for superclass, subclass in kg.subject_objects(RDFS.subClassOf):
        if isinstance(subclass, BNode):
            continue
        print(superclass, subclass)


def get_collection_from_class():
    for _, _, intersection in knowledge_graph.triples((None, OWL.intersectionOf, None)):
        for list_triple in knowledge_graph.triples((intersection, None, None)):
            extract_property_value_from_list(list_triple)
        break


def extract_property_value_from_list(triple):
    _, p, el = triple
    if p == RDF.first:
        edge, node = None, None
        for _, p2, el2 in knowledge_graph.triples((el, None, None)):
            if p2 == OWL.onProperty:
                edge = el2
            if p2 == OWL.hasValue:
                node = el2
        print(edge, node)

    else:
        for list_rest_triple in knowledge_graph.triples((el, None, None)):
            extract_property_value_from_list(list_rest_triple)


# get_all_classes(knowledge_graph)
get_collection_from_class()
