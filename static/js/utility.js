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

function handleFileChange(input) {
    uploadGraph(input.files[0]);
}

function uploadGraph(file) {
    if (!file) {
        console.error('No file selected');
        return;
    }

    console.log('Selected file:', file);

    // Create a FormData object to send the file as multipart/form-data
    let formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            console.log('Upload response:', data);
            if (!data.error) {
                vizGraph(); // Assuming vizGraph() is a function to visualize the graph
            } else {
                createAlert(data.error, "danger");
            }
        })
        .catch(error => console.error('Error:', error));
}

function createAlert(msg, msgType) {
    const alert = document.createElement("div");
    alert.className = 'alert alert-dismissible fade show';
    if (msgType === "danger") {
        alert.classList.add("alert-danger");
    } else if (msgType === "warning") {
        alert.classList.add("alert-warning");
    } else {
        alert.classList.add("alert-dark");
    }

    alert.setAttribute("role", "alert");
    alert.textContent = msg;

    const closeButton = document.createElement("button");
    closeButton.className = "close";
    closeButton.setAttribute("data-dismiss", "alert");
    closeButton.setAttribute("aria-label", "Close");

    const span = document.createElement("span");
    span.setAttribute("aria-hidden", "true");
    span.innerHTML = '&times;';

    closeButton.appendChild(span);

    alert.appendChild(closeButton);

    document.body.insertBefore(alert, document.body.children.item(1));
}