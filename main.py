from flask import Flask, render_template, jsonify
import json
import src.json_parser
import src.graph
import rdflib
from rdflib import Graph, OWL, RDFS, RDF
from rdflib.term import BNode

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/get_graph_data_json')
def get_graph_data_json():

        nodes = []
        edges = []
        with open("C:\Dev\OWLVisualizer\data\mixing_01_2024.jsonld", 'r') as file:
            json_data = json.load(file)
            if isinstance(json_data, list):
                for entry in json_data:
                    #if not any("genid" in key or "genid" in str(value) for key, value in entry.items()) and not \
                    #        any("swrl" in key or "swrl" in str(value) for key, value in entry.items()):
                    if not any("swrl" in key or "swrl" in str(value) for key, value in entry.items()):
                        node_id = entry.get('@id')
                        node_label = entry.get('label', node_id)
                        if '#' in node_label:
                            node_label = node_label.split('#')[-1]  # Extract substring after "#"
                        if node_id:
                            nodes.append({'id': node_id, 'label': node_label, "color": "lime"})
                            if 'http://www.w3.org/2000/01/rdf-schema#subClassOf' in entry:
                                parent_id = entry['http://www.w3.org/2000/01/rdf-schema#subClassOf'][0].get('@id')
                                if parent_id:
                                    edges.append({'from': node_id, 'to': parent_id, 'label': 'subClassOf'})
            else:
                #if not any("genid" in key or "genid" in str(value) for key, value in json_data.items()):
                    node_id = json_data.get('@id')
                    if node_id:
                        nodes.append({'id': node_id, 'label': node_id})
                        if 'http://www.w3.org/2000/01/rdf-schema#subClassOf' in json_data:
                            parent_id = json_data['http://www.w3.org/2000/01/rdf-schema#subClassOf'][0].get('@id')
                            if parent_id:
                                edges.append({'from': node_id, 'to': parent_id, 'label': "subClassOf"})
            # #Alibi genID
            # for entry in json_data:
            #     entry_id = entry.get('@id', '')
            #     entry_type = entry.get('@type', [])
            #     subClassOf = entry.get('http://www.w3.org/2000/01/rdf-schema#subClassOf', [])
            #
            #     if 'http://www.w3.org/2002/07/owl#Class' in entry_type:
            #         parent_id = entry_id
            #         child_id = None
            #         for sub_entry in subClassOf:
            #             sub_entry_id = sub_entry.get('@id', '')
            #             if sub_entry_id.startswith('_:genid'):
            #                 child_id = sub_entry_id  ### Extract the genidXX part
            #                 edges.append({"from": parent_id, "to":child_id})
            #
            # #Alibi genID2
            # for entry in json_data:
            #     entry_id = entry.get('@id', '')
            #     intersectionOf = entry.get('http://www.w3.org/2002/07/owl#intersectionOf', [])
            #     if intersectionOf:
            #         parent_id = entry_id
            #         child_ids = []
            #         for intersection in intersectionOf:
            #             intersection_list = intersection.get('@list', [])
            #             for item in intersection_list:
            #                 sub_entry_id = item.get('@id', '')
            #                 if sub_entry_id.startswith('_:genid'):
            #                     child_id = sub_entry_id  # Extract the genidXX part
            #                     child_ids.append(child_id)
            #                     edges.append({'from': parent_id, 'to': child_id})
            #
            # #Parameters
            # for entry in json_data:
            #     entry_id = entry.get('@id', '')
            #     onProperty = entry.get('http://www.w3.org/2002/07/owl#onProperty', [])
            #
            #     if onProperty:
            #             parent_id = entry_id  # Extract the genidXX part
            #             child_id = onProperty[0].get('@id')  # Extract the property name
            #
            #             edges.append({'from': parent_id, 'to': child_id})
            for item in src.json_parser.get_links_between_parameters_and_classes(file_path="C:\Dev\OWLVisualizer\data\mixing_01_2024.jsonld"):
                edges.append({"from": item["parameter"], "to": item["class"]})
        print(nodes)
        print(edges)
        return jsonify({'nodes': nodes, 'edges': edges})


knowledge_graph = Graph()
knowledge_graph.parse("C:\Dev\OWLVisualizer\data\mixing_01_2024.owl")

@app.route('/get_graph_data_rdf')
def get_graph_data_rdf():
    rdf_graph = src.graph.get_all_classes(knowledge_graph)
    print(rdf_graph[0])
    print(rdf_graph[1])
    return jsonify({'nodes': rdf_graph[0]})


if __name__ == '__main__':
    app.run(debug=True)

