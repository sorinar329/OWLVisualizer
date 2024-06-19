let restrictionIdx = 1;
let fetchedData = null;

let sub = "";
let pred = "";
let obj = "";

function fetchTriplesOnce() {
    return new Promise((resolve, reject) => {
        if (fetchedData) {
            resolve(fetchedData);
        } else {
            fetch(`/query_builder`)
                .then(response => response.json())
                .then(data => {
                    if (data.subjects && data.subjects.length > 0) {
                        fetchedData = data;
                        resolve(data);
                    } else {
                        resolve(null);
                    }
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                    resolve(null);
                });
        }
    });
}

function selectedValue(selectElement, idx) {
    const row = document.getElementById("query-builder-select-row");
    const select2 = row.children.item(1).children[0];
    const select3 = row.children.item(2).children[0];

    if (idx === 1) {
        if (sub !== selectElement.value && sub !== "") {
            sub = selectElement.value;
            select2.classList.add("d-none");
            select2.innerHTML = "";
            select3.classList.add("d-none");
            select3.innerHTML = "";
        }
        sub = selectElement.value;
        selectElement.title = selectElement.options[selectElement.selectedIndex].textContent;

    } else if (idx === 2) {
        if (pred !== selectElement.value) {
            pred = selectElement.value;
            select3.classList.add("d-none");
            select3.innerHTML = "";
        }
        pred = selectElement.value;
        selectElement.title = selectElement.options[selectElement.selectedIndex].textContent;
    } else if (idx === 3) {
        obj = selectElement.value;
        selectElement.title = selectElement.options[selectElement.selectedIndex].textContent;
    } else {

    }
}

function populate_suggestions_triple(selectElement, idx) {
    fetchTriplesOnce().then(data => {
        if (selectElement.innerHTML !== "") {
            return
        }
        selectElement.innerHTML = "";
        let labels;
        let iris;
        let type;
        if (idx === 1) {
            const subjects = data['subjects'];
            labels = subjects.map(subject => {
                return subject['label'];
            });
            iris = subjects.map(subject => {
                return subject['iri'];
            });
            type = subjects.map(subject => {
                return subject['type'];
            });
        } else if (idx === 2) {
            const selectedSubject = data['subjects'].find(subject => subject['iri'] === sub);
            const predicates = selectedSubject['predicates'];
            labels = predicates.map(predicate => {
                return predicate['label'];
            });
            iris = predicates.map(predicate => {
                return predicate['iri'];
            });
            type = predicates.map(subject => {
                return subject['type'];
            });
        } else {
            const selectedSubject = data['subjects'].find(subject => subject['iri'] === sub);
            const selectedPredicate = selectedSubject['predicates'].find(predicate => predicate['iri'] === pred);
            const objects = selectedPredicate['objects'];
            labels = objects.map(object => {
                return object['label'];
            });
            iris = objects.map(object => {
                return object['iri'];
            });
            type = objects.map(subject => {
                return subject['type'];
            });
        }

        const emptyOption = document.createElement('option');
        emptyOption.textContent = '';
        selectElement.appendChild(emptyOption);
        groupOptions(selectElement, idx);

        for (let i = 0; i < labels.length; i++) {
            const optgroup = Array.from(selectElement.getElementsByTagName("optgroup"))
                .find(optgroup => optgroup.label === type[i]);
            if (optgroup) {
                const option = document.createElement('option');
                option.textContent = labels[i];
                option.value = iris[i];
                optgroup.appendChild(option);
            }

        }
    }).catch(error => {
        console.error('Error:', error);
    });
}

function groupOptions(currentSelect, idx) {
    if (idx === 1 || idx === 3) {
        const classOptions = ["Classes", "Restrictions"];
        classOptions.forEach(option => {
                const optgroup = document.createElement("optgroup");
                optgroup.label = option;
                currentSelect.appendChild(optgroup);
            }
        )
    } else {
        const classOptions = ["Is a", "Attributes", "Relations", "Other"];
        classOptions.forEach(option => {
                const optgroup = document.createElement("optgroup");
                optgroup.label = option;
                currentSelect.appendChild(optgroup);
            }
        )
    }
}

function sendSelectedValues() {
    const row = document.getElementById("query-builder-select-row");
    const select1 = row.children.item(0).children[0];
    const select2 = row.children.item(1).children[0];
    const select3 = row.children.item(2).children[0];

    const selectedValues = {
        'firstSelect': encodeURIComponent(select1.value),
        'secondSelect': encodeURIComponent(select2.value),
        'thirdSelect': encodeURIComponent(select3.value)
    };
    fetchedData = null;
    [sub, pred, obj] = ["", "", ""]
    fetch('/query_builder', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({selectedValues}),
    })
        .then(response => response.json())
        .then(data => {
        })
        .catch(error => console.error('Error sending data to server:', error));
}

function deleteRow(button) {
    let row = button.parentNode.parentNode;
    let cardBody = row.parentNode;

    let deleteTriples = [];

    let index = Array.prototype.indexOf.call(cardBody.children, row);

    while (cardBody.children.length > index) {
        row = cardBody.children[index];
        let triples = [];
        for (let j = 0; j < 3; j++) {
            let selectField = row.children.item(j).children[0];
            triples.push(selectField.value);
        }
        deleteTriples.push(triples);
        cardBody.removeChild(row);
    }

    if (cardBody.children.length === 0) {
        let queryBuilderBody = document.getElementById("query-builder-body");
        let card = cardBody.parentNode;
        queryBuilderBody.removeChild(card);
    }

    fetch('/query_builder_clear', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({"clearTriples": deleteTriples}) // Leeres Objekt als Nachricht
    })
        .then(response => {
            if (response.ok) {
                // Erfolgreich gelöscht
                console.log("Cleared triples");
            } else {
                // Fehler beim Löschen
                console.error('Fehler beim Löschen der Triples:', response.statusText);
            }
        })
        .catch(error => {
            console.error('Fehler beim Löschen der Triples:', error);
        });


    console.log(deleteTriples);
}

function clearSelectedOptions() {
    let body = document.getElementById("query-builder-body");
    let selectRow = document.getElementById("query-builder-select-row");
    for (let i = 0; i < 3; i++) {
        let selectField = selectRow.children.item(i).children[0];
        if (i > 0) {
            selectField.classList.add("d-none")
        }
        selectField.innerHTML = '';
    }
    for (let i = 1; i < body.children.length; i++) {
        let child = body.children[i];
        body.removeChild(child);
    }
    fetchedData = null;

    fetch('/query_builder_clear', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({"clearTriples": []}) // Leeres Objekt als Nachricht
    })
        .then(response => {
            if (response.ok) {
                // Erfolgreich gelöscht
                console.log("Cleared triples");
            } else {
                // Fehler beim Löschen
                console.error('Fehler beim Löschen der Triples:', response.statusText);
            }
        })
        .catch(error => {
            console.error('Fehler beim Löschen der Triples:', error);
        });

}


function showSelectFields(row) {
    const select1 = row.children.item(0).children[0];
    const select2 = row.children.item(1).children[0];
    const select3 = row.children.item(2).children[0];
    const button = row.children.item(3).children[0];
    if (select1.value !== "") {
        select2.classList.remove("d-none");
    } else {
        select1.title = "Choose a subject";
        select2.classList.add("d-none");
        select2.innerHTML = "";
        select3.classList.add("d-none");
        select3.innerHTML = "";
    }

    if (select2.value !== "") {
        select3.classList.remove("d-none");
    } else {
        select2.title = "Choose a predicate";
        select3.classList.add("d-none");
        select3.innerHTML = "";
    }
    if (select3.value === "") {
        select3.title = "Choose an object"
        button.classList.add("invisible");
    } else {
        button.classList.remove("invisible");
    }
}

function createGraphDropDown(groupName) {
    const navItem = document.createElement("li");
    navItem.className = "nav-item dropdown";
    navItem.id = groupName + "-navItem";

    const navLink = document.createElement("a");
    navLink.className = "nav-link dropdown-toggle active";

    navLink.setAttribute('data-toggle', 'dropdown');
    navLink.href = "#";
    navLink.setAttribute('role', 'button');
    navLink.setAttribute('aria-haspopup', 'true');
    navLink.setAttribute('aria-expanded', 'false');
    navLink.textContent = groupName;

    const dropDown = document.createElement("div");
    dropDown.id = groupName + "-dropdown";
    dropDown.className = "dropdown-menu";

    const graphItem = document.createElement("a");
    graphItem.id = groupName + "-view";
    graphItem.className = "dropdown-item";
    graphItem.href = "#";
    graphItem.textContent = "View Graph";

    const sparqlItem = document.createElement("a");
    sparqlItem.id = groupName + "-sparql";
    sparqlItem.className = "dropdown-item";
    sparqlItem.href = "#";
    sparqlItem.textContent = "SPARQL Query";

    dropDown.appendChild(graphItem);
    dropDown.appendChild(sparqlItem);

    navItem.appendChild(navLink);
    navItem.appendChild(dropDown);

    const navTab = document.getElementById("query-builder-nav-tab");
    navTab.appendChild(navItem);

    return navItem;
}

function createTabPane(groupName) {
    const tabContent = document.getElementById("query-builder-tab-content");
    let tabPane = document.createElement("div");
    if (document.getElementById(groupName + "-tab") !== null) {
        Array.from(tabPane.children).forEach(child => {
            child.innerHTML = "";
        })
        return;
    }

    tabPane = document.createElement("div");
    tabPane.className = "tab-pane show active";
    tabPane.id = groupName + "-tab";
    tabContent.appendChild(tabPane);

}

function createGraphVizTabContent(row, groupName) {
    fetch('/query_builder_graph_vis')
        .then(response => response.json())
        .then(data => {
            const tabPane = document.getElementById(groupName + "-tab");
            let graphContainer = document.getElementById(groupName + "-network")
            if (graphContainer === null) {
                graphContainer = document.createElement("div");
                graphContainer.id = groupName + "-network";
                graphContainer.className = "vis-network-modal";
                graphContainer.setAttribute("aria-labelledby", groupName + "-view");

                tabPane.appendChild(graphContainer);
                const tabContent = document.getElementById("query-builder-tab-content");
                tabContent.appendChild(tabPane);
            }

            const options = {
                layout: {
                    improvedLayout: true
                },
            };
            const nodesDataset = new vis.DataSet(data.nodes)
            const edgesDataset = new vis.DataSet(data.edges)
            new vis.Network(graphContainer, {nodes: nodesDataset, edges: edgesDataset}, options);

            for (let i = 0; i < 3; i++) {
                let selectField = row.children.item(i).children[0];
                selectField.innerHTML = '';
            }
            showSelectFields(row);
        })
        .catch(error => console.error('Error fetching data:', error));
}

function createSPARQLTabContent(groupName) {
    const textArea = document.createElement("textarea");
    textArea.id = groupName + "-sparql-textarea";
    textArea.className = "form-control";
    textArea.setAttribute("rows", "10");
    textArea.setAttribute("aria-labelledby", groupName + "-sparql");
    textArea.style.display = "None";
    const tab = document.getElementById("Hierarchy-tab");
    tab.appendChild(textArea);
}

function getTripleType(modalBody, row) {
    let sub = row.children.item(0).children[0].value;
    let pred = row.children.item(1).children[0].value;
    let obj = row.children.item(2).children[0].value;
    if (!sub.startsWith("Res") && !obj.startsWith("Res")) {
        if (pred === "subClassOf") {
            return "Hierarchy";
        } else if (pred === "equivalentClass") {
            return "Equivalent Classes";
        }
    } else {
        let tripleType = "Restriction-" + restrictionIdx;
        restrictionIdx++;
        return tripleType;
    }
}