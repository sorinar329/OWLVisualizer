from rdflib import Graph, OWL, RDFS, RDF
from rdflib.term import BNode, URIRef, Literal, Node

# Liste von Tasks
# Liste von Ingredients
# Liste von Containern
# Liste von Tools

# 1. Funktion für die Erstellung der Query für die Tasks DONE
# 2. Funktion für die Erstellung der QUery für die Ingredients DONE
# 3. Funktion für die Erstellung der Query für Tools
# 4. Funktion für die Erstellung der Query für Container

# 5. Funktion für Inferenz  mit Input 1 Ingredient und Liste von Ingredients.
# 6. Funktion für die Datenausgabe der Visualisierung.

knowledge_graph = Graph()
knowledge_graph.parse("static/ontologies/mixing.owl")

def get_tasks():
    task_list = []
    for subj, obj in knowledge_graph.subject_objects(predicate=RDFS.subClassOf):
        if "http://www.ease-crc.org/ont/mixing#Task" in obj:
            task_list.append(str(subj))

    return task_list


def get_ingredients(superclass, knowledge_graph=knowledge_graph):
    ingredients_list = []

    for subj, obj in knowledge_graph.subject_objects(predicate=RDFS.subClassOf):
        if superclass in obj:
            ingredients_list.append(str(subj))
            ingredients_list.extend(get_ingredients(subj))

    return ingredients_list


def check_if_leaf(kg, cls):
    is_superclass = False

    for subj, obj in kg.subject_objects(predicate=RDFS.subClassOf):
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

    for subj, obj in knowledge_graph.subject_objects(predicate=RDFS.subClassOf):
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
        for subj, obj in knowledge_graph.subject_objects(predicate=RDFS.subClassOf):
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

def generate_task_tree():
    first_entry = {"col1": "1", "col2": "Pick up any Tool", "col3": "MixingTool: " + str(get_tool_leaf()[1])}
    second_entry = { 'col1': '2.', 'col2': 'Go to the Container', 'col3': "Container: " + str(get_container_leaf()[1])}
    task_list = [first_entry, second_entry]

    print(task_list)

generate_task_tree()