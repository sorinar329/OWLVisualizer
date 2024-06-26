import rdflib
from owlready2 import *

onto_path = os.path.join(os.getcwd(), 'static/ontologies/mixing.owl')

SOMA = get_namespace("http://www.ease-crc.org/ont/SOMA.owl")
DUL = get_namespace("http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#")
MIXING = get_ontology(onto_path).load()

OBO = get_namespace("http://purl.obolibrary.org/obo/")


def get_tasks():
    tasks = list(DUL['Task'].subclasses())

    return [{'name': task.name, 'label': str(task.label[0])} for task in tasks]


def get_ingredients():
    ingredients = []
    for meta_ingredient in MIXING['Ingredient'].subclasses():
        for meta_ingredient2 in meta_ingredient.subclasses():
            ingredients.extend(list(meta_ingredient2.subclasses()))

    return [{'name': ing.name, 'label': str(ing.label[0])} for ing in ingredients]


def get_containers():
    containers = list(SOMA['Crockery'].descendants())
    containers.remove(SOMA['Crockery'])

    container_names = [cls.name for cls in containers]
    container_iris = [cls.iri for cls in containers]
    return container_iris, container_names


def get_tools():
    tools = list(SOMA['Cutlery'].descendants())
    tools.remove(SOMA['Cutlery'])
    tools.extend(list(MIXING['KitchenTool'].descendants()))
    tools.remove(MIXING['KitchenTool'])

    tool_iris = [tool.iri for tool in tools]
    tool_names = [tool.name for tool in tools]

    return tool_iris, tool_names


def init_graph_to_visualize():
    graph_to_visualize = {'nodes': [], 'edges': []}
    return graph_to_visualize


def generate_task_tree_and_graphdata(task, ingredients):
    motion, parameters, task_instance = get_inference(task, ingredients)

    graph = init_graph_to_visualize()
    nodes = graph.get("nodes")
    edges = graph.get("edges")

    nodes.append({'id': task_instance.name, 'label': task_instance.name,
                  'color': {'background': "#AAF683", "border": "black"},
                  'shapeProperties': {'borderRadius': 10}})
    nodes.append({'id': task_instance.is_a[0].name, 'label': str(task_instance.is_a[0].label[0]),
                  'color': {'background': "#AAF683", "border": "black"}})
    edges.append({'from': task_instance.name, 'to': task_instance.is_a[0].name, 'label': 'is a', 'arrow': 'to'})

    for ing in task_instance.hasIngredient:
        nodes.append({'id': ing.name, 'label': ing.name, 'color': {'background': '#60D394', 'border': 'black'},
                      'shapeProperties': {'borderRadius': 10}})
        nodes.append({'id': ing.is_a[0].name, 'label': str(ing.is_a[0].label[0]),
                      'color': {'background': '#60D394', 'border': 'black'}})
        edges.append({'from': ing.name, 'to': task_instance.name, 'label': 'hasIngredient'})
        edges.append({'from': ing.name, 'to': ing.is_a[0].name, 'label': 'is a', 'arrow': 'to'})

    nodes.append({'id': motion, 'label': motion, 'color': {'background': '#EE6055', 'border': 'black'},
                  'shapeProperties': {'borderRadius': 10}})

    edges.append({'from': task_instance.name, 'to': motion, 'label': 'performMotion'})

    nodes.append({'id': "Container_instance", 'label': "ContainerObject",
                  'color': {"background": "#FF9B85", "border": "black"},
                  'shapeProperties': {'borderRadius': 10}})

    nodes.append({'id': "Container", 'label': "Container", 'color': {"background": "#FF9B85", "border": "black"}})
    nodes.append({'id': "Tool_instance", 'label': "ToolObject", "shape": "box",
                  'shapeProperties': {'borderRadius': 10},
                  'color': {"background": "#FF9B85", "border": "black"}})

    nodes.append({'id': "Tool", 'label': "Tool", 'color': {"background": "#FF9B85", "border": "black"}})

    edges.append({'from': task_instance.name, 'to': "Container_instance", 'label': "hasContainer"})
    edges.append({'from': task_instance.name, 'to': "Tool_instance", 'label': "hasTool"})
    edges.append({'from': "Container_instance", 'to': "Container", 'label': "is a", "arrow": "to"})
    edges.append({'from': "Tool_instance", 'to': "Tool", 'label': "is a", "arrow": "to"})

    for para in parameters:
        nodes.append({'id': str(para["Parameter"]) + '-' + str(para["Value"]), 'label': str(para["Value"]),
                      'color': {"background": "#FFD97D", "border": "black"}})
        edges.append({'from': motion, 'to': str(para["Parameter"]) + '-' + str(para["Value"]),
                      'label': str(para["Parameter"])})

    first_entry = {"col1": "1", "col2": "Pick up any Tool", "col3": "Asserted: MixingTool: " + str(get_tools()[1])}
    second_entry = {'col1': '2.', 'col2': 'Go to the Container',
                    'col3': "Asserted: Container: " + str(get_containers()[1])}
    third_entry = {'col1': '3', 'col2': 'Hold the container with the left arm',
                   'col3': "Asserted Container: " + str(get_containers()[1])}
    fourth_entry = {'col1': '4', 'col2': 'Go on the start position with the right arm for the Motion: ' + motion,
                    'col3': "Infered Motion: " + motion}

    fifth_entry = {'col1': '5', 'col2': 'Execute the Motion: ' + motion + ' with the infered Parameters',
                   'col3': "Infered Parameters: " +
                           str(parameters).replace("]", "").replace("[", "")}

    sixth_entry = {'col1': '6.', 'col2': 'Put the Tool down left to the container',
                   'col3': "Asserted: MixingTool: Any, Container: Any"}

    seventh_entry = {'col1': '7.', 'col2': 'Finish', 'col3': ""}

    task_list = [first_entry, second_entry, third_entry, fourth_entry, fifth_entry, sixth_entry, seventh_entry]

    return task_list, graph


def get_inference(task_name, ingredients):
    task_instance = MIXING[task_name](f"Task Instance")
    ingredients_list = []

    for x in range(len(ingredients)):
        if ingredients[x].startswith("FOODON"):
            ingredient_instance = OBO[ingredients[x]](f"Ingredient-{x}")
        else:
            ingredient_instance = MIXING[ingredients[x]](f"Ingredient-{x}")
        print(f'Created ingredient: {ingredient_instance}')
        ingredients_list.append(ingredient_instance)
        task_instance.hasIngredient.append(ingredient_instance)

    motion = MIXING.Motion("motiontop")
    task_instance.performMotion.append(motion)

    print(list(task_instance.get_properties()))
    # union = set()
    # for ingredient_instance in ingredients_list:
    #     ing_ancestors = set(ingredient_instance.is_a[0].ancestors())
    #     union = union.union(ing_ancestors)
    # intersection1 = set(MIXING.Ingredient.subclasses()).intersection(union)
    # rules = set()
    # for r in MIXING.rules():
    #     body_classes = {pred.class_predicate for pred in r.body}
    #
    #     if len(body_classes.intersection(intersection1)) == len(intersection1) \
    #             and task_instance.is_a[0] in body_classes:
    #         rules.add(r)
    #
    # other_rules = set(MIXING.rules()).difference(rules)
    # for r in other_rules:
    #     destroy_entity(r)

    sync_reasoner_pellet()
    reclassified_motion = motion.is_a[0]
    motion_name = reclassified_motion.name
    motion_parameters = []

    for restriction in reclassified_motion.is_a[1:]:
        if isinstance(restriction, owlready2.Restriction):
            parameter = {'Parameter': restriction.property.name, 'Value': restriction.value}
            motion_parameters.append(parameter)
        if isinstance(restriction, owlready2.class_construct.And) or \
                isinstance(restriction, owlready2.class_construct.Or):
            for el in restriction.is_a:
                parameter = {'Parameter': el.property.name, 'Value': el.value}
                motion_parameters.append(parameter)

    return motion_name, motion_parameters, task_instance

# generate_task_tree_and_graphdata("BeatingTask", ["FOODON_03315102"])
