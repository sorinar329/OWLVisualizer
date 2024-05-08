let graph;

function vizGraph() {
    fetch('/get_graph_data_rdf')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('mynetwork');
            const options = {
                physics: {
                    adaptiveTimestep: true,
                    barnesHut: {
                        gravitationalConstant: -7000,
                        springConstant: 0.04,
                        springLength: 100,
                    },
                    timestep: 0.3
                },
                layout: {
                    improvedLayout: false
                },
            };
            const nodesDataset = new vis.DataSet(data.nodes)
            const edgesDataset = new vis.DataSet(data.edges)
            const network = new vis.Network(container, {nodes: nodesDataset, edges: edgesDataset}, options);
            const searchBar = document.getElementById("searchBar");
            console.log(network);
            searchBar.addEventListener("keyup", function () {
               data = network.body.data.nodes._data;
               autocompleteInput(this, data);
            });


        })
        .catch(error => console.error('Error fetching data:', error));
}

