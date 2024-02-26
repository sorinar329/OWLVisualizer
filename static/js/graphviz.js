function viz_graph() {
    fetch('/get_graph_data_rdf')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('mynetwork');
            const options = {};
            const network = new vis.Network(container, data, options);
        })
        .catch(error => console.error('Error fetching data:', error));
}