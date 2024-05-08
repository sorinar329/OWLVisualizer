function autocompleteInput(searchBar, data) {
    searchBar.addEventListener('input', function () {
        const inputValue = searchBar.value.toLowerCase(); // Den Eingabewert der Suchleiste in Kleinbuchstaben umwandeln
        const matchingLabels = Object.values(data)
            .filter(nodeData => nodeData.label.toLowerCase().includes(inputValue))
            .map(nodeData => nodeData.label);
        console.log(matchingLabels);
    });
}