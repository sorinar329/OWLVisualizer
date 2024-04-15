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


def get_ingredients(knowledge_graph, superclass):
    ingredients_list = []

    for subj, obj in knowledge_graph.subject_objects(predicate=RDFS.subClassOf):
        if superclass in obj:
            ingredients_list.append(str(subj))
            ingredients_list.extend(get_ingredients(knowledge_graph, subj))

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
    for item in get_ingredients(knowledge_graph, superclass="http://www.ease-crc.org/ont/mixing#Ingredient"):
        leaf.append(check_if_leaf(knowledge_graph, item))

    filtered_leaf = list(filter(lambda x: x is not None, leaf))
    return filtered_leaf


#print(get_ingredients_leaf())


