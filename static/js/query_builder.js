let restrictionIdx = 1;
let fetchedData = null;

let sub = null;
let pred = null;
let obj = null;

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

function selectedValue(selectElement) {
    const row = document.getElementById("query-builder-select-row");
    const selects = row.querySelectorAll('select');
    let idx = Array.prototype.indexOf.call(selects, selectElement) + 1;
    console.log("Called selectedVAlue")
    if (idx === 1) {
        sub = selectElement.value;
        selectElement.title = sub;
    } else if (idx === 2) {
        pred = selectElement.value;
        selectElement.title = pred;
    } else {
        obj = selectElement.value
        selectElement.title = obj;
    }
}

function populate_suggestions_triple(selectElement, idx) {
    fetchTriplesOnce().then(data => {
        if (selectElement.value !== "") {
            return
        }

        let labels;
        let iris;
        let type;
        console.log(idx)
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
        const classOptions = ["Classes", "Instances", "Restrictions", "Other"];
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
    fetch('/query_builder', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({selectedValues}),
    })
        .then(response => response.json())
        .then(data => {
            // Handle the response from the server
        })
        .catch(error => console.error('Error sending data to server:', error));

    document.getElementById("query-builder-run").classList.remove("invisible");
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
        select2.selectedIndex = -1;
        select3.classList.add("d-none");
        select3.selectedIndex = -1;
    }

    if (select2.value !== "") {
        select3.classList.remove("d-none");
    } else {
        select2.title = "Choose a predicate";
        select3.classList.add("d-none");
        select3.selectedIndex = -1;
    }
    if (select3.value === "") {
        select3.title = "Choose an object"
        button.classList.add("invisible");
    } else {
        button.classList.remove("invisible");
    }
}


function createGroupedTripleCard(modalBody, groupName) {
    const card = document.createElement("div");
    card.className = "card";
    card.id = groupName;
    card.title = groupName

    const cardHeader = document.createElement("div");
    cardHeader.className = "card-header";
    cardHeader.id = "cardHeader" + (modalBody.children.length);

    const header = document.createElement("h4");
    header.className = "card-title";
    header.id = "cardTitle" + (modalBody.children.length);
    header.textContent = groupName;

    const cardBody = document.createElement("div");
    cardBody.className = "card-body";
    cardBody.id = "cardBody" + (modalBody.children.length);


    cardHeader.appendChild(header);
    card.appendChild(cardHeader);
    card.appendChild(cardBody);
    modalBody.appendChild(card);

    return card
}

function displaySelectedTriples(rowName, lengthChildren) {
    const newSelectRow = document.createElement("div");
    newSelectRow.className = "row";
    newSelectRow.id = rowName.title + "-" + "select-row" + (lengthChildren + 1);

    const deleteCol = document.createElement("div");
    deleteCol.className = "col-auto";

    const deleteButton = document.createElement("button");
    deleteButton.className = "btn btn-danger btn-sm";
    deleteButton.id = "button" + (lengthChildren + 1);
    deleteButton.title = "Delete";
    deleteButton.innerHTML = '<i class="bi bi-x-lg"></i>';
    deleteButton.addEventListener("click", function () {
        deleteRow(this);
    });

    deleteCol.appendChild(deleteButton);
    for (let i = 0; i < 3; i++) {

        const newSelect = document.createElement("select");
        newSelect.className = "custom-select custom-select-sm";
        newSelect.disabled = true;
        newSelect.id = rowName.title + "-" + "select" + ((3 * lengthChildren) + (i + 1));

        const newSelectContainer = document.createElement("div");
        newSelectContainer.className = "col";
        newSelectContainer.appendChild(newSelect);

        newSelectRow.appendChild(newSelectContainer);
    }

    newSelectRow.appendChild(deleteCol);
    return newSelectRow;
}

function transferInputToGroup(row, card) {

    const cardBody = card.getElementsByClassName("card-body")[0];
    const groupRow = displaySelectedTriples(card.title, cardBody.children.length);

    for (let i = 0; i < 3; i++) {
        let selectField = row.children.item(i).children[0];
        let groupSelectField = groupRow.children.item(i).children[0]
        const option = document.createElement('option');
        option.value = selectField.value;
        option.textContent = selectField.options[selectField.selectedIndex].textContent;
        groupSelectField.appendChild(option);

        groupSelectField.title = option.textContent;
        selectField.innerHTML = '';

    }

    cardBody.appendChild(groupRow);
    showSelectFields(row);
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
        if (!sub.startsWith("Res") && obj.startsWith("Res")) {
            let tripleType = "Restriction-" + restrictionIdx;
            restrictionIdx++;
            return tripleType;
        } else if (sub.startsWith("Res")) {
            let cards = modalBody.getElementsByClassName("card");
            for (let i = 0; i < cards.length; i++) {
                let cardBody = cards[i].getElementsByClassName("card-body")[0];
                let selectRows = cardBody.getElementsByClassName("row");
                for (let j = 0; j < selectRows.length; j++) {
                    let selectFields = selectRows[j].getElementsByTagName("select");
                    for (let k = 0; k < selectFields.length; k++) {
                        if (selectFields[k].value === sub) {
                            return cards[i].id;
                        }
                    }
                }
            }
        }
    }

}