document.getElementById("forecast-form").addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent default form submission

    const formData = new FormData(event.target); // Collect form data
    fetch('/forecast', {
        method: 'POST',
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            // Update the graph
            const plotImg = document.getElementById("forecast-plot");
            plotImg.src = "data:image/png;base64," + data.plot;

            // Update the forecast table
            const tableBody = document.getElementById("forecast-table-body");
            tableBody.innerHTML = ""; // Clear previous data

            data.forecast_data.forEach(row => {
                const tr = document.createElement("tr");

                const tdDate = document.createElement("td");
                tdDate.textContent = row.date;

                const tdCount = document.createElement("td");
                tdCount.textContent = row.job_count;

                tr.appendChild(tdDate);
                tr.appendChild(tdCount);
                tableBody.appendChild(tr);
            });
        })
        .catch(error => console.error('Error:', error));
});

// Download Graph
document.getElementById("download-plot").addEventListener("click", function () {
    const formData = new FormData(document.getElementById("forecast-form"));
    fetch('/download_plot', {
        method: 'POST',
        body: formData,
    })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'forecast_plot.png';
            link.click();
        })
        .catch(error => console.error('Error:', error));
});

// Download CSV
document.getElementById("download-csv").addEventListener("click", function () {
    const formData = new FormData(document.getElementById("forecast-form"));
    fetch('/download_csv', {
        method: 'POST',
        body: formData,
    })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'forecast_data.csv';
            link.click();
        })
        .catch(error => console.error('Error:', error));
});
