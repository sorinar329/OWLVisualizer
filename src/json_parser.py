import json

def count_jsonld_entries(file_path):
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
            if isinstance(json_data, list):
                return len(json_data)
            else:
                return 1  # If it's not a list, consider it as a single entry
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return 0
    except json.JSONDecodeError:
        print(f"Invalid JSON format in file '{file_path}'.")
        return 0

import json

def filter_jsonld_entries_without_swrl(file_path):
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
            if isinstance(json_data, list):
                for entry in json_data:
                    if "swrl" not in json.dumps(entry):
                        print(entry)
            else:
                if "swrl" not in json.dumps(json_data):
                    print(json_data)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except json.JSONDecodeError:
        print(f"Invalid JSON format in file '{file_path}'.")

def filter_jsonld_entries_with_only_class(file_path):
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
            if isinstance(json_data, list):
                for entry in json_data:
                    if len(entry.keys()) == 1 and "Class" in entry:
                        print(entry)
            else:
                if len(json_data.keys()) == 1 and "Class" in json_data:
                    print(json_data)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except json.JSONDecodeError:
        print(f"Invalid JSON format in file '{file_path}'.")

import json

def filter_jsonld_entries_with_specific_structure(file_path):
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
            if isinstance(json_data, list):
                for entry in json_data:
                    if isinstance(entry, dict) and \
                            len(entry.keys()) == 3 and \
                            '@id' in entry and \
                            '@type' in entry and \
                            isinstance(entry['@type'], list) and \
                            'http://www.w3.org/2002/07/owl#Class' in entry['@type']:
                        print(entry)
            else:
                if isinstance(json_data, dict) and \
                        len(json_data.keys()) == 3 and \
                        '@id' in json_data and \
                        '@type' in json_data and \
                        isinstance(json_data['@type'], list) and \
                        'http://www.w3.org/2002/07/owl#Class' in json_data['@type']:
                    print(json_data)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except json.JSONDecodeError:
        print(f"Invalid JSON format in file '{file_path}'.")

def get_graph_data():

        nodes = []
        edges = []
        with open("C:\Dev\OWLVisualizer\data\mixingjson.jsonld", 'r') as file:
            json_data = json.load(file)
            if isinstance(json_data, list):
                for entry in json_data:
                    if not any("genid" in key or "genid" in str(value) for key, value in entry.items()) and not \
                            any("swrl" in key or "swrl" in str(value) for key, value in entry.items()):
                        node_id = entry.get('@id')
                        if node_id:
                            nodes.append({'id': node_id, 'label': node_id})
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


get_graph_data()
# Example usage:
file_path = "C:\Dev\OWLVisualizer\data\mixingjson.jsonld"
#filter_jsonld_entries_with_specific_structure(file_path)