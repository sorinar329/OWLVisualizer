// Solution found at: https://stackoverflow.com/questions/59503468/prevent-bootstrap-form-to-submit-with-enter
$("form").keypress(function (e) {
    if (e.keyCode === 13) {
        e.preventDefault();
        return false;
    }
})

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
            data = network.body.data.nodes._data;
            autocompleteInput(data);
            const searchButton = document.getElementById("searchButton");
            searchButton.addEventListener("click", function () {
                viewNode(network, data);
            });
            searchBar.addEventListener("keypress", function (event) {
                if (event.key === "Enter") {
                    viewNode(network, data);
                }
            })


        })
        .catch(error => console.error('Error fetching data:', error));
}

