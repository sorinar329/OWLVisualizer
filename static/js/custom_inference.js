function customInference() {
    // Verify that the graphContainer exists
        const container = document.getElementById('graphContainer');
        if (!container) {
            console.error("Graph container not found!");
            return;
        }

        // Initialize the graph
        const data = {
            nodes: [],
            edges: []
        };
        const options = {
            edges: {
                color: {
                    inherit: false
                }
            }
        }; // Customize graph options if needed
        const network = new vis.Network(container, data, options);


        function updateGraphAndTable(graphData, tableData) {
            // Update graph
            const container = document.getElementById('graphContainer');
            if (!container) {
                console.error("Graph container not found!");
                return;
            }

            const data = {
                nodes: graphData.nodes,
                edges: graphData.edges
            };
            const options = {
                edges: {
                    color: {
                        inherit: false
                    }
                }
            }; // Customize graph options if needed
            const network = new vis.Network(container, data, options);

            // Update table
            const tableBody = document.getElementById('tableBody');
            tableBody.innerHTML = ''; // Clear previous content
            tableData.forEach(rowData => {
                const row = document.createElement('tr');
                row.innerHTML = `
            <td>${rowData.col1}</td>
            <td>${rowData.col2}</td>
            <td>${rowData.col3}</td>
        `;
                tableBody.appendChild(row);
            });

            // Show the modal after a short delay to ensure the graph is rendered properly
            setTimeout(function () {
                $('#graphTableModal').modal('show');
            }, 100);
        }

        jQuery(document).ready(function ($) {
            // Function to fetch and populate tasks
            $.ajax({
                url: '/task_ingredients',
                type: 'GET',
                success: function (data) {
                    var taskSelect = $('#taskSelect');
                    $.each(data.tasks, function (index, task) {
                        taskSelect.append($('<option>', {
                            value: task,
                            text: task.split("#")[1]
                        }));
                    });
                    var ingredientSelect = $('#ingredientSelect');
                    $.each(data.ingredients, function (index, ingredient) {
                        ingredientSelect.append($("<option>", {
                            value: ingredient,
                            text: ingredient.split("#")[1]

                        }));
                    });
                }
            });
        });


        document.getElementById('addIngredientField').addEventListener('click', function () {
            var originalSelect = document.getElementById('ingredientSelect');
            var newSelect = originalSelect.cloneNode(true);
            newSelect.id = 'ingredientSelect' + Math.floor(Math.random() * 1000); // Generate unique ID for the new select
            originalSelect.parentNode.appendChild(newSelect);
        });
        $(document).on('click', '#customModal .modal-footer .btn-primary', function () {
            var task = $("#taskSelect").val();
            console.log("Task:", task);

            // Retrieve selected values from all ingredient select fields
            var ingredients = [];
            $('.modal-body .form-group select').each(function () {
                var ingredient = $(this).val();
                if (ingredient && ingredient !== task) {
                    ingredients.push(ingredient);
                }
            });

            // Log the ingredients array to check if task is included
            console.log("Ingredients:", ingredients);

            // Create a data object to send to the backend
            var data = {
                task: task,
                ingredients: ingredients
            };

            // Send an AJAX POST request to your Flask backend
            $.ajax({
                type: "POST",
                url: "/data",
                data: JSON.stringify(data),
                contentType: "application/json",
                success: function (response) {
                    // Handle the response from the server
                    const graphData = response.graphData;
                    const tableData = response.tableData;
                    updateGraphAndTable(graphData, tableData);
                },
                error: function (err) {
                    // Handle errors if any
                    console.error('There was a problem fetching data:', err);
                }
            });
        });
    }