from flask import Flask, render_template, jsonify, request
import graph.graph
import graph.coloring
import query_builder

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/get_graph_data_rdf')
def get_graph_data_rdf():
    graph_visualize = graph.graph.get_graph_to_visualize()
    graph.coloring.color_classes(graph_visualize)
    graph.coloring.color_parameters(graph_visualize)
    return jsonify({'nodes': graph_visualize.get("nodes"), 'edges': graph_visualize.get("edges")})


@app.route('/suggest_classes', methods=["GET"])
def suggest_classes():
    graph_visualize = graph.graph.get_graph_to_visualize()
    classes = [i.get('id') for i in graph_visualize.get("nodes")]
    print(classes)
    return jsonify(classes)

@app.route('/query_builder', methods=["GET"])
def suggest_triples():
    qb = query_builder.get_query_builder()
    suggestions = qb.mock_suggestion2()
    selected_option = request.args.get('selectedOption')
    return jsonify(suggestions)


if __name__ == '__main__':
    app.run(debug=True)
