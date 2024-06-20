from flask import Flask, render_template, jsonify, request
import graph.graph
from query_builder import query_builder
from urllib.parse import unquote

app = Flask(__name__)
kg_instance = graph.graph.KnowledgeGraph('data/mixing.owl')
qb = query_builder.get_query_builder(kg_instance)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/get_graph_data_rdf')
def get_graph_data_rdf():
    # kg_instance = graph.graph.KnowledgeGraph('data/food_cutting.owl')
    graph_visualize = kg_instance.get_graph_to_visualize()
    print(f"Num nodes: {len(graph_visualize.get('nodes'))}")
    print(f"Num edges: {len(graph_visualize.get('edges'))}")
    return jsonify({'nodes': graph_visualize.get("nodes"), 'edges': graph_visualize.get("edges")})


@app.route('/query_builder', methods=["GET", "POST"])
def suggest_triples():
    if request.method == 'POST':
        print("Received data")
        response = request.json['selectedValues']
        triple = [unquote(response['firstSelect']), unquote(response['secondSelect']), unquote(response['thirdSelect'])]
        qb.set_triple(triple)
        #print(triple)
        return jsonify("suggestions")

    else:
        print("sending data")
        while True:
            suggestions = qb.mock_suggestion2()
            print(len(suggestions.get("subjects")))
            if len(suggestions.get('subjects')) > 0:
                break
        return jsonify(suggestions)


@app.route('/query_builder_clear', methods=['POST'])
def clear_triples():
    response = request.json
    print(response['clearTriples'])
    qb.clear_triples(response['clearTriples'])
    return jsonify({'message': 'Cleared triples'}), 200


@app.route('/query_builder_redirect')
def redirect2_query_builder_vis():
    return render_template('queryBuilderViz.html')


@app.route('/query_builder_graph_vis', methods=["GET", "POST"])
def visualize_query_builder_filtered_graph():
    if qb.has_suggestions():
        graph_visualize = qb.get_partial_viz_graph()
        return jsonify({'nodes': graph_visualize.get("nodes"), 'edges': graph_visualize.get("edges")})


if __name__ == '__main__':
    app.run(debug=True)
