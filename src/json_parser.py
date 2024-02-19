import json

file_path = "C:\Dev\OWLVisualizer\data\mixing_01_2024.jsonld"


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


def filter_entries_with_specific_format(file_path):
    with open(file_path, 'r') as file:
        json_data = json.load(file)
        for entry in json_data:
            entry_id = entry.get('@id', '')
            entry_type = entry.get('@type', [])
            subClassOf = entry.get('http://www.w3.org/2000/01/rdf-schema#subClassOf', [])

            if 'http://www.w3.org/2002/07/owl#Class' in entry_type:
                for sub_entry in subClassOf:
                    sub_entry_id = sub_entry.get('@id', '')
                    if sub_entry_id.startswith('_:genid'):
                        print(entry)
                        break


def declare_parent_child_relationships(file_path):
    with open(file_path, 'r') as file:
        json_data = json.load(file)
        for entry in json_data:
            entry_id = entry.get('@id', '')
            entry_type = entry.get('@type', [])
            subClassOf = entry.get('http://www.w3.org/2000/01/rdf-schema#subClassOf', [])

            if 'http://www.w3.org/2002/07/owl#Class' in entry_type:
                parent_id = entry_id
                child_id = None
                for sub_entry in subClassOf:
                    sub_entry_id = sub_entry.get('@id', '')
                    if sub_entry_id.startswith('_:genid'):
                        child_id = sub_entry_id  ### Extract the genidXX part
                        break

                if child_id:
                    print(f"Parent: {parent_id}, Child: {child_id}")


def declare_parent_child_relationship(file_path):
    relationships = []
    with open(file_path, 'r') as file:
        json_data = json.load(file)
        for entry in json_data:
            entry_id = entry.get('@id', '')
            intersectionOf = entry.get('http://www.w3.org/2002/07/owl#intersectionOf', [])
            if intersectionOf:
                parent_id = entry_id
                child_ids = []
                for intersection in intersectionOf:
                    intersection_list = intersection.get('@list', [])
                    for item in intersection_list:
                        sub_entry_id = item.get('@id', '')
                        if sub_entry_id.startswith('_:genid'):
                            child_id = sub_entry_id.split('_')[-1]  # Extract the genidXX part
                            child_ids.append(child_id)

                for child_id in child_ids:
                    relationships.append({'parent': parent_id, 'child': child_id})

                print(parent_id)
                print(child_id)

    return relationships


def declare_parent_child_relationships2(file_path):
    relationships = []
    with open(file_path, 'r') as file:
        json_data = json.load(file)
        for entry in json_data:
            entry_id = entry.get('@id', '')
            onProperty = entry.get('http://www.w3.org/2002/07/owl#onProperty', [])

            if onProperty:
                parent_id = entry_id  # Extract the genidXX part
                child_id = onProperty[0].get('@id')  # Extract the property name
                print(parent_id)
                print(child_id)
                relationships.append({'parent': parent_id, 'child': child_id})

    return relationships


# Example usage:
def get_genID_of_parameter(file_path):
    with open(file_path, 'r') as file:
        json_data = json.load(file)
        list_of_properties = []
        for entry in json_data:
            entry_id = entry.get('@id', '')
            onProperty = entry.get('http://www.w3.org/2002/07/owl#onProperty', [])
            if onProperty:
                list_of_properties.append(entry_id)

        return list_of_properties


def find_property_from_genID(file_path, genID):
    with open(file_path, 'r') as file:
        json_data = json.load(file)

        # Find the entry with the given genID
        for entry in json_data:
            entry_id = entry.get('@id', '')
            if entry_id == f'{genID}':
                onProperty = entry.get('http://www.w3.org/2002/07/owl#onProperty', [])
                if onProperty:
                    return onProperty[0].get('@id', '')

        return None  # GenID not found or no onProperty entry found


def is_id_in_intersection(file_path, target_id):
    with open(file_path, 'r') as file:
        json_data = json.load(file)

        # Iterate through each entry
        for entry in json_data:
            entry_id = entry.get('@id', '')
            intersectionOf = entry.get('http://www.w3.org/2002/07/owl#intersectionOf', [])
            if intersectionOf:
                intersection_list = intersectionOf[0].get('@list', [])
                for item in intersection_list:
                    item_id = item.get('@id', '')
                    if item_id == f'{target_id}':
                        return entry_id

        return False  # ID not found in any intersection


def is_genid_subclass_of(file_path, target_genid):
    with open(file_path, 'r') as file:
        json_data = json.load(file)

        # Iterate through each entry
        for entry in json_data:
            entry_id = entry.get('@id', '')
            subclassOf = entry.get('http://www.w3.org/2000/01/rdf-schema#subClassOf', [])
            for subclass_entry in subclassOf:
                subclass_id = subclass_entry.get('@id', '')
                if subclass_id == f'{target_genid}':
                    return entry_id

        return False  # genid not found as a subclassOf in any entry


def get_links_between_parameters_and_classes(file_path):
    class_parameters_list = []  # Initialize an empty list to store dictionaries
    for item in get_genID_of_parameter(file_path):
        parameter_dict = {}  # Create a dictionary for each parameter
        parameter_dict['parameter'] = find_property_from_genID(file_path, item)
        parameter_class = is_genid_subclass_of(file_path, is_id_in_intersection(file_path, item))
        if parameter_class:
            parameter_dict['class'] = parameter_class
            class_parameters_list.append(parameter_dict)  # Append the dictionary to the list

    return class_parameters_list

