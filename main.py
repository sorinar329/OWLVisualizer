from flask import Flask, render_template, jsonify
import src.graph.graph
import src.graph.coloring
from src.graph.graph_utility import uri_or_literal_2label

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/get_graph_data_rdf')
def get_graph_data_rdf():
    graph_visualize = src.graph.graph.get_graph_to_visualize()
    src.graph.coloring.color_classes(graph_visualize)
    src.graph.coloring.color_parameters(graph_visualize)
    return jsonify({'nodes': graph_visualize.get("nodes"), 'edges': graph_visualize.get("edges")})


@app.route('/suggest_classes', methods=["GET"])
def suggest_classes():
    graph_visualize = src.graph.graph.get_graph_to_visualize()
    classes = [i.get('id') for i in graph_visualize.get("nodes")]
    print(classes)
    return jsonify(classes)


if __name__ == '__main__':
    app.run(debug=True)
