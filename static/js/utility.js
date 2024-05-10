function autocompleteInput(nodes) {
    console.log(nodes);
    if (typeof nodes !== 'object' || nodes === null) {
        console.error('Invalid input for nodes.');
        return;
    }

    const dataList = document.getElementById("datalistOptions");
    if (!dataList) {
        console.error('Data list element not found.');
        return;
    }

    dataList.innerHTML = '';
    let ids = Object.values(nodes).map(nodeData => nodeData.id);
    let labels = Object.values(nodes).map(nodeData => nodeData.label);
    for (let i = 0; i < labels.length; i++) {
        let opt = document.createElement("option");
        if (ids[i].startsWith("Res")) {
            continue;
        }
        opt.value = labels[i];
        dataList.appendChild(opt);
    }
}

function viewNode(network, nodes) {
    const searchBar = document.getElementById("searchBar");
    let selectedNode = searchBar.value;
    let nodesData = Object.values(nodes);
    let nodeId = nodesData.filter(node => node.label === selectedNode).map(node => node.id);
    searchBar.value = "";


    const options = {
        scale: 1.2,
        animation: {
            duration: 1000,
            easingFunction: 'easeInOutQuad'
        }
    };
    network.setSelection({nodes: [nodeId]});
    network.focus(nodeId, options);
}
