from rdflib import Graph
from src.graph.graph_utility import get_all_actions_tasks, get_all_dispositions, get_all_cutting_tools, \
    get_all_soma_tools, get_all_motions

"""
Using the following color palette: https://coolors.co/palette/ee6055-60d394-aaf683-ffd97d-ff9b85
"""


def color_classes(graph: dict):
    nodes = [n for n in graph.get("nodes") if 'Motion' in n.get("id")]
    for motion in nodes:
        motion.update({'color': {"background": "#FF9B85", "border": "black"}})
    nodes = [n for n in graph.get("nodes") if 'Motion' not in n.get("id") and 'Task' not in n.get("id")]
    for node in nodes:
        if node['label'] == "Thing":
            continue
        node.update({"color": "#60D394", "border": "black"})


def color_motions(kg: Graph, graph: dict):
    classes = set()
    get_all_motions(kg, classes)
    nodes = graph.get("nodes")
    nodes = [x for x in nodes if x.get('id') in classes]
    for cls in nodes:
        cls.update({'color': {"background": "#EE6055", "border": "black"}})


def color_parameters(graph: dict):
    for node in graph.get("nodes"):
        if node.get('id').startswith('Res'):
            node.update({'color': {"background": "#FFD97D", "border": "black"}})


def color_edges(graph: dict):
    for edge in graph.get('edges'):
        edge.update({'color': {'color': 'black'}})


def color_tasks_actions(kg: Graph, graph: dict):
    classes = set()
    get_all_actions_tasks(kg, classes)
    nodes = graph.get("nodes")
    nodes = [x for x in nodes if x.get('id') in classes]
    for cls in nodes:
        cls.update({'color': {"background": "#AAF683", "border": "black"}})


def color_dispositions(kg: Graph, graph: dict):
    classes = set()
    get_all_dispositions(kg, classes)
    nodes = graph.get("nodes")
    nodes = [x for x in nodes if x.get('id') in classes]
    for cls in nodes:
        cls.update({'color': {"background": "#EE6055", "border": "black"}})


def color_tools(kg: Graph, graph: dict):
    classes = set()
    get_all_cutting_tools(kg, classes)
    get_all_soma_tools(kg, classes)
    nodes = graph.get("nodes")
    nodes = [x for x in nodes if x.get('id') in classes]
    for cls in nodes:
        cls.update({'color': {"background": "#FF9B85", "border": "black"}})


def color_instances(graph: dict):
    instances = [x.get("from") for x in graph.get("edges") if x.get("label") == 'is a']
    nodes = graph.get("nodes")
    nodes = [x for x in nodes if x.get('id') in instances]
    for instance in nodes:
        instance.update(
            {'color': {"background": "#EE6055", "border": "black", "borderWidth": 1, "borderWidthSelected": 3}})
