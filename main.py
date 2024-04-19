from flask import Flask, render_template, jsonify, request
import src.graph.graph
import src.graph.coloring
import os
from rdflib import Graph, OWL, RDFS, RDF
from src.graph import coloring
from src.graph import graph
from src import inference_builder
#import query_builder

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("homepage.html")


@app.route("/owlviz")
def owlviz():
    return render_template("index.html")

cached_data = None
cached_status = False
data_path = "C:\Dev\OWLVisualizer\data"
@app.route('/get_graph_data_rdf')
def get_graph_data_rdf():
    global cached_data
    global cached_status
    file_path = [os.path.join(data_path, file) for file in
                 os.listdir(data_path)]

    knowledge_graph = Graph()
    knowledge_graph.parse(file_path[0])
    if not cached_status:
        if cached_data is None:

            graph_visualize = graph.get_graph_to_visualize(knowledge_graph)
            coloring.color_classes(graph_visualize)
            coloring.color_parameters(graph_visualize)
            cached_data = {'nodes': graph_visualize.get("nodes"), 'edges': graph_visualize.get("edges")}
            cached_status = True
            return jsonify(cached_data)
    if cached_status:
        graph_visualize = graph.get_graph_to_visualize(knowledge_graph)
        coloring.color_classes(graph_visualize)
        coloring.color_parameters(graph_visualize)
        cached_data_new = {'nodes': graph_visualize.get("nodes"), 'edges': graph_visualize.get("edges")}

        return jsonify(cached_data_new)


@app.route('/suggest_classes', methods=["GET"])
def suggest_classes():
    graph_visualize = graph.get_graph_to_visualize()
    classes = [i.get('id') for i in graph_visualize.get("nodes")]
    return jsonify(classes)

#
# @app.route('/query_builder', methods=["GET"])
# def suggest_triples():
#     qb = query_builder.get_query_builder()
#     suggestions = qb.mock_suggestion2()
#     selected_option = request.args.get('selectedOption')
#     return jsonify(suggestions)


@app.route('/upload', methods=['POST'])
def upload_file_graph():
    # Delete existing files in the folder
    folder_path = data_path
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            return jsonify({'error'})

    # Save the new uploaded file
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    file.save(os.path.join(folder_path, file.filename))

    return jsonify({'filename': file.filename})

@app.route("/task_ingredients")
def get_tasks_and_ingredients():
    return jsonify({"tasks": inference_builder.get_tasks(), "ingredients": inference_builder.get_ingredients_leaf()})
    #return jsonify({"tasks": ["Stirring", "Mixing"], "ingrdients": ["A", "B"]})



# graphData = {
#     "nodes": [
#         { "id": 1, "label": "Ingredients", "color": "lightgreen"},
#         { "id": 2, "label": "Wet Ingredients", "color": "lightgreen" },
#         { "id": 3, "label": "Egg", "color": "lightgreen" },
#         { "id": 4, "label": "Task", "color": "red" },
#         { "id": 5, "label": "MixingTask", "color": "red" },
#         { "id": 6, "label": "VerticalCircular", "color": "red" },
#         { "id": 7, "label": "WhirlstormMotion", "color": "red" },
#         { "id": 8, "label": "radiuslower: 0.0", "color": "yellow" },
#         { "id": 9, "label": "radiusupper: 0.7", "color": "yellow" },
#         { "id": 10, "label": "radiusupper: 0.7", "color": "yellow" },
#         { "id": 11, "label": "radiuslower: 0.0", "color": "yellow" }
#     ],
#     "edges": [
#         { "from": 1, "to": 2 },
#         { "from": 2, "to": 3 },
#         { "from": 4, "to": 5 },
#         { "from": 5, "to": 6 },
#         { "from": 5, "to": 7 },
#         { "from": 6, "to": 8 },
#         { "from": 6, "to": 9 },
#         { "from": 7, "to": 10 },
#         { "from": 7, "to": 11 }
#     ]
# }
#



@app.route('/save_data', methods=['POST'])
def handle_data():
    data = request.json
    task = data.get('task')
    ingredient = data.get('ingredients')

    return task, ingredient

@app.route('/data', methods=['GET', 'POST'])
def get_data():
    data = request.json
    task = data.get('task')
    ingredients = data.get('ingredients')
    task_tree, graphData = inference_builder.generate_task_tree_and_graphdata(task, ingredients)
    #task = "http://www.ease-crc.org/ont/mixing#BeatingTask"
    # ingredients = ["http://www.ease-crc.org/ont/mixing#Milk", "http://www.ease-crc.org/ont/mixing#Butter", "http://www.ease-crc.org/ont/mixing#Flour"]
    #ingredients = ["http://www.ease-crc.org/ont/mixing#Butter"]
    return jsonify({"graphData": graphData, "tableData": task_tree})

if __name__ == '__main__':
    app.run(debug=True)