#from rdflib import Graph, OWL, RDFS, RDF
import rdflib
from rdflib.term import BNode, URIRef, Literal, Node
from owlready2 import *


knowledge_graph = rdflib.Graph()
knowledge_graph.parse("static/ontologies/mixing.owl")
SOMA = get_ontology("http://www.ease-crc.org/ont/SOMA.owl")

def get_tasks():
    task_list = []
    for subj, obj in knowledge_graph.subject_objects(predicate=rdflib.RDFS.subClassOf):
        if "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Task" in obj:
            task_list.append(str(subj))

    return task_list


def get_ingredients(superclass, knowledge_graph=knowledge_graph):
    ingredients_list = []

    for subj, obj in knowledge_graph.subject_objects(predicate=rdflib.RDFS.subClassOf):
        if superclass in obj:
            ingredients_list.append(str(subj))
            ingredients_list.extend(get_ingredients(subj))

    return ingredients_list


def check_if_leaf(kg, cls):
    is_superclass = False

    for subj, obj in kg.subject_objects(predicate=rdflib.RDFS.subClassOf):
        if cls in obj:
            is_superclass = True
            break

    if not is_superclass:
        return cls


def get_ingredients_leaf():
    leaf = []
    for item in get_ingredients(superclass="http://www.ease-crc.org/ont/mixing#Ingredient"):
        leaf.append(check_if_leaf(knowledge_graph, item))

    filtered_leaf = list(filter(lambda x: x is not None, leaf))
    return filtered_leaf


def get_container(superclass, kg=knowledge_graph):
    container_list = []

    for subj, obj in knowledge_graph.subject_objects(predicate=rdflib.RDFS.subClassOf):
        if superclass in obj:
            container_list.append(str(subj))
            container_list.extend(get_container(subj))

    return container_list

def get_container_leaf():
    leaf = []
    leaf_label = []
    for item in get_container(superclass="http://www.ease-crc.org/ont/SOMA.owl#TableWare"):
        leaf.append(check_if_leaf(knowledge_graph, item))

    filtered_leaf = list(filter(lambda x: x is not None, leaf))
    for i in filtered_leaf:
        leaf_label.append(i.split("#")[1])
    return filtered_leaf, leaf_label




def get_tool(superclass, kg=knowledge_graph):
    tool_list = []
    for item in superclass:
        for subj, obj in knowledge_graph.subject_objects(predicate=rdflib.RDFS.subClassOf):
            if item in obj:
                tool_list.append(str(subj))
                tool_list.extend(get_container(subj))

    return tool_list



def get_tool_leaf():
    leaf = []
    leaf_label = []
    for item in get_tool(["Cutlery", "KitchenTool"]):
        leaf.append(check_if_leaf(knowledge_graph, item))

    filtered_leaf = list(filter(lambda x: x is not None, leaf))
    for i in filtered_leaf:
        leaf_label.append(i.split("#")[1])
    return filtered_leaf, leaf_label

def init_graph_to_visualize():
    graph_to_visualize = {'nodes': [], 'edges': []}
    return graph_to_visualize

def generate_task_tree_and_graphdata(task, ingredients):

    motion, parameters, task_instance = get_inference(task, ingredients)

    graph = init_graph_to_visualize()
    nodes = set()
    for property in task_instance.get_properties():
        for value in property[task_instance]:
            nodes.add(value)
            graph.get("edges").append({'from': task_instance.name, 'to': value.name, 'label': property.name})
            for cls in value.is_a:
                if property.name == "hasIngredient":
                    graph.get("edges").append({"from": cls.name, "to": cls.is_a[0].name, 'label': "subClassOf"})
                    nodes.add(cls.is_a[0])
                graph.get("edges").append({'from': cls.name, 'to': "Thing", 'label': "subClassOf"})
                graph.get("edges").append({'from': value.name, 'to': cls.name, 'label': "is a"})
                nodes.add(cls)

    graph.get("edges").append({'from': task_instance.name, 'to': task_instance.is_a[0].name, 'label': "is a" })
    nodes.add(task_instance.is_a[0])
    nodes.add(task_instance)

    for node in nodes:
        graph.get("nodes").append({'id': node.name, 'label': node.name})

    graph.get("nodes").append({'id': "Container_instance", 'label': "ContainerObject", "color": "lightgreen"})
    graph.get("nodes").append({'id': "Container", 'label': "Container", "color": "lightgreen"})
    graph.get("nodes").append({'id': "Tool_instance", 'label': "ToolObject", "color": "lightgreen"})
    graph.get("nodes").append({'id': "Tool", 'label': "Tool", "color": "lightgreen"})

    graph.get("edges").append({'from': task_instance.name, 'to': "Container_instance", 'label': "hasContainer" })
    graph.get("edges").append({'from': task_instance.name, 'to': "Tool_instance", 'label': "hasTool" })
    graph.get("edges").append({'from': "Container_instance", 'to': "Container", 'label': "is a", "arrow": "to"  })
    graph.get("edges").append({'from': "Tool_instance", 'to': "Tool", 'label': "is a", "arrow": "to" })

    for para in parameters:
        graph.get("nodes").append({'id': str(para["Parameter"]), 'label': str(para["Parameter"]),"color": "yellow"})
        graph.get("edges").append({'from': str(para["Parameter"]), 'to': str(motion), 'label': "subClassOf"})
        graph.get("nodes").append({'id': str(para["Value"]), 'label': str(para["Value"]), "color": "orange"})
        graph.get("edges").append({'from': str(para["Parameter"]), 'to':str(para["Value"]), 'label': "value"})

    first_entry = {"col1": "1", "col2": "Pick up any Tool", "col3": "Asserted: MixingTool: " + str(get_tool_leaf()[1])}
    second_entry = { 'col1': '2.', 'col2': 'Go to the Container', 'col3': "Asserted: Container: " + str(get_container_leaf()[1])}
    third_entry = {'col1': '3', 'col2': 'Hold the container with the left arm', 'col3': "Asserted Container: " + str(get_container_leaf()[1])}
    fourth_entry = {'col1': '4', 'col2': 'Go on the start position with the right arm for the Motion: ' + motion,
                    'col3' : "Infered Motion: " + motion}

    fifth_entry = {'col1': '5', 'col2': 'Execute the Motion: ' + motion + ' with the infered Parameters', 'col3': "Infered Parameters: " +
                                                                                                   str(parameters).replace("]","").replace("[", "")}

    sixth_entry = {'col1': '6.', 'col2': 'Put the Tool down left to the container', 'col3':"Asserted: MixingTool: Any, Container: Any"}

    seventh_entry ={'col1': '7.', 'col2': 'Finish', 'col3': ""}

    task_list = [first_entry, second_entry, third_entry, fourth_entry, fifth_entry, sixth_entry, seventh_entry]

    return task_list, graph



def get_inference(task, ingredients):
    onto = get_ontology("C:\Dev\OWLVisualizer\static\ontologies\mixing.owl").load()
    task_name = task.split("#")[1]
    task_instance = onto[task_name](f"{task_name}-1")
    ingredients_list = []
    for i in ingredients:
        ingredient = i.split("#")[1]
        ingredient_instance = onto[ingredient](f"{ingredient}-1")
        ingredients_list.append(ingredient_instance)
        task_instance.hasIngredient.append(ingredient_instance)

    motion = onto.Motion("motiontop")
    task_instance.performMotion.append(motion)
    union = set()
    for ingredient_instance in ingredients_list:
        ing_ancestors = set(ingredient_instance.is_a[0].ancestors())
        union = union.union(ing_ancestors)
    intersection1 = set(onto.Ingredient.subclasses()).intersection(union)
    rules = set()
    for r in onto.rules():
        body_classes = {pred.class_predicate for pred in r.body}

        if len(body_classes.intersection(intersection1)) == len(intersection1) \
                and task_instance.is_a[0] in body_classes:
            rules.add(r)

    other_rules = set(onto.rules()).difference(rules)
    for r in other_rules:
        destroy_entity(r)

    sync_reasoner(infer_property_values=True)
    a = motion.is_a[0]
    motion = a.name
    triples = []
    get_restrictions_recursive(rdflib.URIRef(a.iri), triples)
    parameters = []

    temp_dict = {}
    for item in triples:
        if isinstance(item[1], rdflib.term.URIRef) and str(item[1]).endswith("onProperty"):
            temp_dict["Parameter"] = str(item[2]).split("#")[-1]  # Extract parameter name from URI
        elif isinstance(item[1], rdflib.term.URIRef) and str(item[1]).endswith("hasValue"):
            temp_dict["Value"] = str(item[2])
            parameters.append(temp_dict.copy())  # Add a copy of temp_dict to result list
            temp_dict.clear()  # Clear temp_dict for the next set of entries



    return motion, parameters, task_instance

def get_restrictions_recursive(node, triples):
    for s, p, o in knowledge_graph.triples((node, None, None)):
        if p == rdflib.OWL.onProperty or p == rdflib.OWL.hasValue:
            triples.append([s,p,o])
        if isinstance(o, rdflib.term.BNode):
            get_restrictions_recursive(o, triples)





