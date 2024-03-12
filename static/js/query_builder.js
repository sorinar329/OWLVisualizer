function fetchTriples() {
    return fetch(`/query_builder`)
        .then(response => response.json())
        .then(data => {
            if (data.subjects && data.subjects.length > 0) {
                return data;
            } else {
                return null;
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            return null;
        });
}

function populate_suggestions_triple(data, row) {
    const select1 = row.children.item(0).children[0];
    const select2 = row.children.item(1).children[0];
    const select3 = row.children.item(2).children[0];

    let currentSelect;
    let labels;
    let iris;
    let type;
    let idx;

    if (select1.value === '') {
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
        currentSelect = select1;
        idx = 1;
    } else if (select2.value === '') {
        const selectedSubject = data['subjects'].find(subject => subject['iri'] === select1.value);
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
        currentSelect = select2
        idx = 2;
    } else {

        const selectedSubject = data['subjects'].find(subject => subject['iri'] === select1.value);
        const selectedPredicate = selectedSubject['predicates'].find(predicate => predicate['iri'] === select2.value);
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
        currentSelect = select3;
        idx = 3;

    }

    currentSelect.innerHTML = '';
    const emptyOption = document.createElement('option');
    const emptyOptionText = document.createTextNode('');
    emptyOption.appendChild(emptyOptionText);
    currentSelect.appendChild(emptyOption);
    groupOptions(currentSelect, idx);
    for (let i = 0; i < labels.length; i++) {
        const optgroup = Array.from(currentSelect.getElementsByTagName("optgroup"))
            .find(optgroup => optgroup.label === type[i]);
        if (optgroup) {
            console.log("Found matching group");
            const newOption = document.createElement('option');
            const optionText = document.createTextNode(labels[i]);
            newOption.appendChild(optionText);
            newOption.setAttribute('value', iris[i]);
            optgroup.appendChild(newOption);
        } else {
            console.log("Didn't find matching group");
            console.log(type[i]);
        }
    }
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
    } else{
        const classOptions = ["Equivalent To", "SubClassOf", "Is a", "Attributes", "Relations", "Other"];
        classOptions.forEach(option => {
                const optgroup = document.createElement("optgroup");
                optgroup.label = option;
                currentSelect.appendChild(optgroup);
            }
        )
    }
}

function sendSelectedValues(row) {
    const select1 = row.children.item(0).children[0];
    const select2 = row.children.item(1).children[0];
    const select3 = row.children.item(2).children[0];

    const selectedValues = [
        encodeURIComponent(select1.value),
        encodeURIComponent(select2.value),
        encodeURIComponent(select3.value)
    ];

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
            console.log('Server response:', data);
        })
        .catch(error => console.error('Error sending data to server:', error));
}


function clearSelectedOptions() {
    let body = document.getElementById("query-builder-body")
    body.innerHTML = '';
}

// Event listener for modal close event
$('#exampleModalCenter').on('hidden.bs.modal', function (e) {
    clearSelectedOptions();
    queryBuilder();
});

function showSelectFields(row) {
    const select1 = row.children.item(0).children[0];
    const select2 = row.children.item(1).children[0];
    const select3 = row.children.item(2).children[0];

    if (select1.value !== "") {
        select2.classList.remove("d-none");
    } else {
        select2.classList.add("d-none");
        select2.selectedIndex = -1;
        select3.classList.add("d-none");
        select3.selectedIndex = -1;
    }

    if (select2.value !== "") {
        select3.classList.remove("d-none");
    } else {
        select3.classList.add("d-none");
        select3.selectedIndex = -1;
    }
}

function createSelectRow() {
    const body = document.getElementById("query-builder-body");
    const newSelectRow = document.createElement("div");
    newSelectRow.className = "row";
    newSelectRow.id = "select-row" + (body.children.length + 1);

    const newButton = document.createElement("button");
    newButton.className = "btn btn-primary";
    newButton.id = "button" + (body.children.length + 1);
    newButton.style.display = "none";
    newButton.textContent = '+';

    for (let i = 0; i < 3; i++) {

        const newSelect = document.createElement("select");
        newSelect.className = "custom-select custom-select-sm d-none";
        if (i === 0) {
            newSelect.classList.remove("d-none")
        }
        newSelect.id = "select" + ((3 * body.children.length) + (i + 1));

        const newSelectContainer = document.createElement("div");
        newSelectContainer.className = "col";
        newSelectContainer.appendChild(newSelect);

        newSelectRow.appendChild(newSelectContainer);
    }
    newSelectRow.appendChild(newButton);
    body.appendChild(newSelectRow);
    return newSelectRow;
}


function queryBuilder() {
    fetchTriples().then(data => {
        const row = createSelectRow();

        const select1 = row.children.item(0).children[0];
        const select2 = row.children.item(1).children[0];
        const select3 = row.children.item(2).children[0];
        const button = row.children.item(3);

        if (select1 && select2 && select3) {
            select1.addEventListener('click', function () {
                showSelectFields(row);
                populate_suggestions_triple(data, row);
            });

            select2.addEventListener('click', function () {
                showSelectFields(row);
                populate_suggestions_triple(data, row);
            });

            select3.addEventListener('change', function () {
                sendSelectedValues(row);
                button.style.display = "inline-block";
                button.addEventListener("click", function () {
                    queryBuilder();
                    button.disabled = true;
                });
            });
        }
    }).catch(error => {
        console.error('Error:', error);
    });
}