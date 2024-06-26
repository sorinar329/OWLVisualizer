import os
from urllib.parse import unquote

from flask import Flask, render_template, jsonify, request
from src.graph.graph import KnowledgeGraph
from src.query_builder import query_builder, sparql_generator
from src import inference_builder
from src.query_builder.query_builder import QueryBuilder

app = Flask(__name__)
kg_instance = None
qb = None

cached_data = None
cached_status = False
data_path = "data"

@app.route('/')
def index():
    return render_template("homepage.html")


@app.route("/owlviz")
def owlviz():
    return render_template("index.html")

@app.route('/get_graph_data_rdf')
def get_graph_data_rdf():
    global kg_instance, qb

    file_paths = [os.path.join(data_path, file) for file in
                  os.listdir(data_path)]
    file = file_paths[0]
    kg_instance = KnowledgeGraph(file)
    graph_visualize = kg_instance.get_graph_to_visualize()
    qb = query_builder.get_query_builder(kg_instance)
    print(f"Num nodes: {len(graph_visualize.get('nodes'))}")
    print(f"Num edges: {len(graph_visualize.get('edges'))}")
    return jsonify({'nodes': graph_visualize.get("nodes"), 'edges': graph_visualize.get("edges")})


@app.route('/query_builder', methods=["GET", "POST"])
def suggest_triples():
    if qb is not None and isinstance(qb, QueryBuilder):
        if request.method == 'POST':
            print("Received data")
            response = request.json['selectedValues']
            triple = [unquote(response['firstSelect']), unquote(response['secondSelect']),
                      unquote(response['thirdSelect'])]
            qb.set_triple(triple)
            # print(triple)
            return jsonify("suggestions")

        else:
            print("sending data")
            while True:
                suggestions = qb.mock_suggestion2()
                print(len(suggestions.get("subjects")))
                if len(suggestions.get('subjects')) > 0:
                    break
            return jsonify(suggestions)


@app.route("/task_ingredients")
def get_tasks_and_ingredients():
    return jsonify({"tasks": inference_builder.get_tasks(), "ingredients": inference_builder.get_ingredients()})


@app.route('/upload', methods=['POST'])
def upload_file_graph():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if not file.filename.endswith('.owl'):
        return jsonify({'error': 'The file extension is not .owl'})
    # Delete existing files in the folder
    folder_path = data_path
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            return jsonify({'error'})

    file.save(os.path.join(folder_path, file.filename))

    return jsonify({'filename': file.filename})


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
    task_tree, graph_data = inference_builder.generate_task_tree_and_graphdata(task, ingredients)
    return jsonify({"graphData": graph_data, "tableData": task_tree})


@app.route('/query_builder_clear', methods=['POST'])
def clear_triples():
    if isinstance(qb, QueryBuilder):
        qb.clear_triples()
        return jsonify({'message': 'Cleared triples'}), 200


@app.route('/query_builder_graph_vis', methods=["GET", "POST"])
def visualize_query_builder_filtered_graph():
    if isinstance(qb, QueryBuilder) and qb.has_suggestions():
        graph_visualize = qb.get_partial_viz_graph()
        return jsonify({'nodes': graph_visualize.get("nodes"), 'edges': graph_visualize.get("edges")})


@app.route('/sparql_query_generator')
def send_sparql_query():
    if isinstance(kg_instance, KnowledgeGraph) and isinstance(qb, QueryBuilder):
        sparql_gen = sparql_generator.SparqlGenerator(kg_instance.get_rdflib_graph())
        triples = qb.get_latest_triples()
        sparql_query = sparql_gen.generate_sparql_query(triples)
        return jsonify(sparql_query)

if __name__ == '__main__':
    app.run(debug=True)
