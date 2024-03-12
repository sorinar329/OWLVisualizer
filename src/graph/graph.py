from rdflib import Graph, OWL, RDFS, RDF
from rdflib.term import BNode, URIRef, Literal, Node
from typing import Union
from src.graph.graph_utility import extract_restriction, is_restriction2, is_list2, extract_collection_recursive
import random

knowledge_graph = Graph()
knowledge_graph.parse("data/food_cutting.owl")

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


def uri_or_literal_2label(node: Union[URIRef, Literal, Node]) -> str:
    if isinstance(node, Literal):
        return str(node)
    elif isinstance(node, URIRef):
        if '#' in str(node):
            return str(node).split('#')[-1]
        else:
            return str(node).split('/')[-1]


def extract_collection_members(triple, parent_node):
    _, p, el = triple
    if p == RDF.first:
        edge, node = None, None
        for _, p2, el2 in knowledge_graph.triples((el, None, None)):
            if p2 == OWL.onProperty:
                edge = el2
            if p2 in restriction_type:
                node = el2
        if isinstance(node, BNode) and is_restriction(node):
            return
            # extract_nested_restrictions(node)
        else:
            node_id = f'{node}_{random.randint(0, 10000)}'
            edge = uri_or_literal_2label(edge)
            graph_to_visualize.get("nodes").append({'id': node_id, 'label': uri_or_literal_2label(node)})

            graph_to_visualize.get("edges").append({'from': node_id, 'to': parent_node, 'label': edge})

    else:
        for list_rest_triple in knowledge_graph.triples((el, None, None)):
            extract_collection_members(list_rest_triple, parent_node)


def extract_nested_restrictions(bnode: BNode):
    for _, p, el in knowledge_graph.triples((bnode, None, None)):
        if p == OWL.onProperty:
            print(el)

        if p in restriction_type:
            print(el)
            if isinstance(el, BNode) and is_restriction(el):
                extract_nested_restrictions(el)


def is_list(bnode: BNode):
    for _, _, c in knowledge_graph.triples((bnode, None, None)):
        for p in knowledge_graph.predicates(c):
            if p == RDF.first:
                return True
    return False


def is_restriction(bnode: BNode):
    matched_triple = list(knowledge_graph.triples((bnode, RDF.type, OWL.Restriction)))
    return len(matched_triple) > 0


def get_class_restrictions(knowledge_graph):
    classes_with_restrictions = [(_, res) for (_, res)
                                 in knowledge_graph.subject_objects(RDFS.subClassOf)
                                 if isinstance(res, BNode)]
    i = 0
    for x, y in classes_with_restrictions:
        for bnode, p, bnode_or_value in knowledge_graph.triples((y, None, None)):
            if is_restriction(bnode=bnode):
                continue
                # extract_nested_restrictions(bnode=bnode)
            else:
                if collection_type.get(p) is not None:
                    parent_node = f"{collection_type.get(p)[0]}-{i}"

                    graph_to_visualize.get("nodes").append({'id': parent_node, 'label': parent_node})
                    graph_to_visualize.get("edges").append({'from': str(x), 'to': str(parent_node),
                                                            'label': collection_type.get(p)[1]})
                    extract_collection_members((None, p, bnode_or_value), parent_node)
                    i += 1


def get_class_restrictions2(knowledge_graph):
    classes_with_restrictions = [res for (_, res)
                                 in knowledge_graph.subject_objects(RDFS.subClassOf)
                                 if isinstance(res, BNode)]
    i = 0
    for restrictions in classes_with_restrictions:
        for triple in knowledge_graph.triples((restrictions, None, None)):
            # if is_restriction2(knowledge_graph, triple[2]):
            #     print("Is restriction")
            if is_list2(knowledge_graph, triple[2]):
                for triple2 in knowledge_graph.triples((triple[2], None, None)):
                    print(extract_collection_recursive(knowledge_graph, triple2))
            # else:
            #     print("Is URIRef")
            #     print(triple[2])
            # if is_restriction2(knowledge_graph, triple[0]):
            #     for triple2 in knowledge_graph.triples((triple[2], None, None)):
            #         if triple[1] == OWL.onProperty:
            #             print(triple[2])
            #         for triple3 in knowledge_graph.triples((triple2[2],None, None)):
            #             if triple3[1] == RDF.first:
            #                 print(triple3[2])
                # val = extract_restriction(knowledge_graph, triple[0])
                # if is_list2(knowledge_graph, val[1]):
                #     print("List: {}".format(val[1]))
                #     for triple2 in knowledge_graph.triples((val[1], None, None)):
                #         extract_collection_recursive(knowledge_graph, triple2)
                # else:
                #     print("Res: {}".format(val))


            # else:
            #     continue
            # if is_restriction(bnode=bnode):
            #     continue
            #     # extract_nested_restrictions(bnode=bnode)
            # else:
            #     if collection_type.get(p) is not None:
            #         parent_node = f"{collection_type.get(p)[0]}-{i}"
            #
            #         graph_to_visualize.get("nodes").append({'id': parent_node, 'label': parent_node})
            #         graph_to_visualize.get("edges").append({'from': str(x), 'to': str(parent_node),
            #                                                 'label': collection_type.get(p)[1]})
            #         extract_collection_members((None, p, bnode_or_value), parent_node)
            #         i += 1


# def equivalent_properties(kg):
#    for triple in kg.triples((None, OWL.equivalentClass, None)):
# if is_list2(knowledge_graph, node=triple[2]):
#     for _, _, o in kg.triples((triple[2], None, None)):
#         if is_list2(knowledge_graph, o):
#             for list_triple in kg.triples((o, None, None)):
#                 pred, obj = extract_collection_recursive(knowledge_graph, list_triple)
#                 print(pred, obj)
# if is_restriction2(knowledge_graph, node=triple[2]):
#     print(triple[0])
#     pred, obj = extract_restriction(knowledge_graph, triple[2])
# graph_to_visualize.get("edges").append({'from': str(cls), 'to': str(parent_node),
#                                         'label': uri_or_literal_2label(pred)})


def get_graph_to_visualize():
    get_all_classes(knowledge_graph)
    get_class_restrictions2(knowledge_graph)
    # return graph_to_visualize


def get_classes():
    return get_all_classes(knowledge_graph)


get_graph_to_visualize()
