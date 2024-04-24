function viz_graph() {
    fetch('/get_graph_data_rdf')
        .then(response => response.json())
        .then(data => {
            console.log(data);
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
            var network = new vis.Network(container, {nodes: nodesDataset, edges: edgesDataset}, options);
            network.on("selectEdge", function (params) {
                var selectedEdgeId = params.edges[0];
                var selectedEdge = edgesDataset.get(selectedEdgeId);
                console.log(selectedEdge);
            });
            //
            //
            // var highlightActive = false;
            // const nodesDatasetOriginal = new vis.DataSet(data.nodes)
            // var nodesDataset = new vis.DataSet(data.nodes);
            // var edgesDataset = new vis.DataSet(data.edges);
            // const allNodesOriginal = nodesDatasetOriginal.get({returnType: "Object"})
            //
            // function redrawAll() {
            //     var container = document.getElementById("mynetwork");
            //     var data = {nodes: nodesDataset, edges: edgesDataset};
            //
            //     network = new vis.Network(container, data, options);
            //
            //     // get a JSON object
            //     allNodes = nodesDataset.get({returnType: "Object"});
            //
            //
            //     network.on("click", neighbourhoodHighlight);
            // }
            //
            // function neighbourhoodHighlight(params) {
            //     if (params.nodes.length > 0) {
            //         highlightActive = true;
            //         var i, j;
            //         var selectedNode = params.nodes[0];
            //         var degrees = 2;
            //
            //         // mark all nodes as hard to read.
            //         for (var nodeId in allNodes) {
            //             allNodes[nodeId].color = "rgba(200,200,200,0.5)";
            //             if (allNodes[nodeId].hiddenLabel === undefined) {
            //                 allNodes[nodeId].hiddenLabel = allNodes[nodeId].label;
            //                 allNodes[nodeId].label = undefined;
            //             }
            //         }
            //
            //         var connectedNodes = network.getConnectedNodes(selectedNode);
            //         var allConnectedNodes = [];
            //
            //         // get the second degree nodes
            //         for (i = 1; i < degrees; i++) {
            //             for (j = 0; j < connectedNodes.length; j++) {
            //                 allConnectedNodes = allConnectedNodes.concat(
            //                     network.getConnectedNodes(connectedNodes[j])
            //                 );
            //             }
            //         }
            //         // all second degree nodes get a different color and their label back
            //         for (i = 0; i < allConnectedNodes.length; i++) {
            //             allNodes[allConnectedNodes[i]].color = "rgba(150,150,150,0.75)";
            //             if (allNodes[allConnectedNodes[i]].hiddenLabel !== undefined) {
            //                 allNodes[allConnectedNodes[i]].label =
            //                     allNodes[allConnectedNodes[i]].hiddenLabel;
            //                 allNodes[allConnectedNodes[i]].hiddenLabel = undefined;
            //             }
            //         }
            //         // all first degree nodes get their own color and their label back
            //         for (i = 0; i < connectedNodes.length; i++) {
            //             allNodes[connectedNodes[i]].color = undefined;
            //             if (allNodes[connectedNodes[i]].hiddenLabel !== undefined) {
            //                 allNodes[connectedNodes[i]].label =
            //                     allNodes[connectedNodes[i]].hiddenLabel;
            //                 allNodes[connectedNodes[i]].hiddenLabel = undefined;
            //             }
            //         }
            //         // the main node gets its own color and its label back.
            //         allNodes[selectedNode].color = undefined;
            //         if (allNodes[selectedNode].hiddenLabel !== undefined) {
            //             allNodes[selectedNode].label = allNodes[selectedNode].hiddenLabel;
            //             allNodes[selectedNode].hiddenLabel = undefined;
            //         }
            //     } else if (highlightActive === true) {
            //         // reset all nodes
            //
            //         allNodes = JSON.parse(JSON.stringify(allNodesOriginal)); // Deep copy
            //         for (var nodeId in allNodes) {
            //             if (allNodes[nodeId].color === undefined) {
            //                 allNodes[nodeId].color = "lightblue"
            //             }
            //             if (allNodes[nodeId].hiddenLabel !== undefined) {
            //                 allNodes[nodeId].label = allNodes[nodeId].hiddenLabel;
            //                 allNodes[nodeId].hiddenLabel = undefined;
            //             }
            //         }
            //         highlightActive = false;
            //     }
            //     var updateArray = [];
            //     for (nodeId in allNodes) {
            //         if (allNodes.hasOwnProperty(nodeId)) {
            //             updateArray.push(allNodes[nodeId]);
            //         }
            //     }
            //     nodesDataset.update(updateArray);
            // }
            //
            //
            // redrawAll()
        })
        .catch(error => console.error('Error fetching data:', error));
}