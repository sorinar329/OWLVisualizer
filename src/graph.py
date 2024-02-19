import rdflib
from rdflib import Graph, OWL, RDFS, RDF
from rdflib.term import BNode

knowledge_graph = Graph()
knowledge_graph.parse("data/mixing.owl")

graph_to_visualize = {'nodes': [], 'edges': []}

restriction_type = [OWL.hasValue, OWL.someValuesFrom, OWL.allValuesFrom]
collection_type = {OWL.intersectionOf: 'Intersection', OWL.unionOf: 'Union'}


def get_all_classes(kg: Graph):
    nodes = set()
    for subclass, superclass in kg.subject_objects(RDFS.subClassOf):
        if isinstance(superclass, BNode):
            continue
        nodes.add(str(subclass))
        nodes.add(str(superclass))
        graph_to_visualize.get("edges").append({'from': str(subclass), 'to': str(superclass), 'label': 'subClassOf'})
    for node in nodes:
        label = node.split("#")[-1]
        graph_to_visualize.get("nodes").append({'id': str(node), 'label': label})


def extract_collection_members(triple, parent_node, count):
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
        graph_to_visualize.get("nodes").append({'id': count, 'label': str(node)})
        graph_to_visualize.get("edges").append({'from': str(node), 'to': str(parent_node), 'label': str(edge)})
        count += 1
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
                    parent_node = f"Intersection-{i}"

                    graph_to_visualize.get("nodes").append({'id': parent_node, 'label': parent_node})
                    graph_to_visualize.get("edges").append({'from': str(x), 'to': str(parent_node), 'label': str(parent_node)})
                    extract_collection_members((None, p, bnode_or_value), parent_node)
                    i += 1


def equivalent_properties(kg):
    for cls, p, cls_or_bnode in kg.triples((None, OWL.equivalentClass, None)):
        if is_restriction(bnode=cls_or_bnode):
            extract_nested_restrictions(cls_or_bnode)


def get_graph_to_visualize():
    get_all_classes(knowledge_graph)
    get_class_restrictions(knowledge_graph)
    return graph_to_visualize
