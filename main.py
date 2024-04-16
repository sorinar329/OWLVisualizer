from flask import Flask, render_template, jsonify, request
import graph.graph
from query_builder import query_builder
from urllib.parse import unquote

app = Flask(__name__)
qb = query_builder.get_query_builder()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/get_graph_data_rdf')
def get_graph_data_rdf():
    kg_instance = graph.graph.KnowledgeGraph('data/food_cutting.owl')
    graph_visualize = kg_instance.get_graph_to_visualize()
    print(f"Num nodes: {len(graph_visualize.get('nodes'))}")
    print(f"Num edges: {len(graph_visualize.get('edges'))}")
    return jsonify({'nodes': graph_visualize.get("nodes"), 'edges': graph_visualize.get("edges")})


@app.route('/suggest_classes', methods=["GET"])
def suggest_classes():
    graph_visualize = graph.graph.get_graph_to_visualize()
    classes = [i.get('id') for i in graph_visualize.get("nodes")]
    return jsonify(classes)


@app.route('/query_builder', methods=["GET", "POST"])
def suggest_triples():
    if request.method == 'POST':
        print("Received data")
        print(f"Chosen object {unquote(request.json['selectedValues'][2])}")
        triple = [unquote(el) for el in request.json['selectedValues']]
        qb.set_triple(triple)
        return jsonify(qb.mock_suggestion2())
    else:
        print("sending data")
        suggestions = qb.mock_suggestion2()
        return jsonify(suggestions)


if __name__ == '__main__':
    app.run(debug=True)
