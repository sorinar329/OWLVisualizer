from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/get_graph_data')
def get_graph_data():
    try:
        nodes = []
        edges = []
        with open("C:\Dev\OWLVisualizer\data\mixingjson.jsonld", 'r') as file:
            json_data = json.load(file)
            if isinstance(json_data, list):
                for entry in json_data:
                    if not any("genid" in key or "genid" in str(value) for key, value in entry.items()) and not \
                            any("swrl" in key or "swrl" in str(value) for key, value in entry.items()):
                        node_id = entry.get('@id')
                        node_label = entry.get('label', node_id)
                        if '#' in node_label:
                            node_label = node_label.split('#')[-1]  # Extract substring after "#"
                        if node_id:
                            nodes.append({'id': node_id, 'label': node_label})
                            if 'http://www.w3.org/2000/01/rdf-schema#subClassOf' in entry:
                                parent_id = entry['http://www.w3.org/2000/01/rdf-schema#subClassOf'][0].get('@id')
                                if parent_id:
                                    edges.append({'from': node_id, 'to': parent_id})
            else:
                if not any("genid" in key or "genid" in str(value) for key, value in json_data.items()):
                    node_id = json_data.get('@id')
                    if node_id:
                        nodes.append({'id': node_id, 'label': node_id})
                        if 'http://www.w3.org/2000/01/rdf-schema#subClassOf' in json_data:
                            parent_id = json_data['http://www.w3.org/2000/01/rdf-schema#subClassOf'][0].get('@id')
                            if parent_id:
                                edges.append({'from': node_id, 'to': parent_id})

            print(nodes)
            print(edges)
        return jsonify({'nodes': nodes, 'edges': edges})
    except FileNotFoundError:
        return jsonify({'error': 'File not found'})
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON format'})


if __name__ == '__main__':
    app.run(debug=True)

