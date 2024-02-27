function populate_suggestions_triple() {
    fetch('/query_builder')
        .then(response => response.json())
        .then(data => {
            const select1 = document.getElementById('select1');
            select1.innerHTML = ''; // Leeren des vorhandenen Inhalts

            for (let i = 0; i < data.length; i++) {
                const newOption = document.createElement('option');
                const optionText = document.createTextNode(data[i][0]);
                newOption.appendChild(optionText);
                newOption.setAttribute('value', data[i][0]);
                select1.appendChild(newOption);
            }
        })
        .catch(error => console.error('Error fetching data:', error));
}

function showSelectFields() {
        var select1 = document.getElementById("select1");
        var select2Group = document.getElementById("select2");
        var select3Group = document.getElementById("select3");

        if (select1.value !== "") {
            select2Group.classList.remove("d-none");
            select3Group.classList.add("d-none");
        } else {
            select2Group.classList.add("d-none");
            select3Group.classList.add("d-none");
        }
    }

function showThirdSelect() {
    var select2 = document.getElementById("select2");
    var select3Group = document.getElementById("select3");

    if (select2.value !== "") {
        select3Group.classList.remove("d-none");
    } else {
        select3Group.classList.add("d-none");
    }
}

//Should be used to implement filtering the graph ?
function filter() {

}