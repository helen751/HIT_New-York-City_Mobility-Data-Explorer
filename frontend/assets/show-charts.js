let tripsChart = null;

// Getting the available dates automatically and setting the most recent date as default
async function loadAvailableDates() {

    const response = await fetch("http://127.0.0.1:5000/api/available-dates");
    const dates = await response.json();

    const select = document.getElementById("chartDatePicker");
    select.innerHTML = "";

    dates.forEach(date => {
        const option = document.createElement("option");
        option.value = date;
        option.textContent = date;
        select.appendChild(option);
    });

    // Automatically loading most recent date
    if (dates.length > 0) {
        loadTripsChart(dates[0]);
    }
}


// Loading trips for selected date hourly
async function loadTripsChart(date) {

    const start = date + " 00:00:00";
    const end = date + " 23:59:59";

    const response = await fetch(
        `http://127.0.0.1:5000/api/trips-over-time?start=${start}&end=${end}&group=hour`
    );

    const data = await response.json();

    // Creating 24-hour array filled and initialize trip counts to 0 for each hour
    const hours = Array.from({length: 24}, (_, i) => i);
    const tripCounts = new Array(24).fill(0);

    data.forEach(item => {
        tripCounts[item.time_label] = item.trip_count;
    });

    renderChart(hours, tripCounts);
}

// Render chart
function renderChart(labels, values) {

    const ctx = document.getElementById("tripsChart").getContext("2d");

    if (tripsChart) {
        tripsChart.destroy();
    }

    tripsChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Trips per Hour",
                data: values,
                backgroundColor: "#4f7cff"
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    title: { display: true, text: "Hour of Day" }
                },
                y: {
                    title: { display: true, text: "Number of Trips" },
                    beginAtZero: true
                }
            }
        }
    });
}


// function to render line graph for all line graph metrics (trips, revenue, avg fare over time)
let metricChart = null;

function renderLineGraph(labels, values, metricLabel) {

    const ctx = document.getElementById("metricChart").getContext("2d");

    if (metricChart) {
        metricChart.destroy();
    }

    // plotting the line graph with Chart.js
    metricChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: metricLabel,
                data: values,
                borderColor: "#4f7cff",
                backgroundColor: "rgba(79,124,255,0.1)",
                fill: true,
                tension: 0.3,
                pointRadius: 2
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "Date"
                    }
                },
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: metricLabel
                    }
                }
            }
        }
    });
}

document.getElementById("metricSelector")
    .addEventListener("change", function () {
        loadTimeMetric(this.value);
    });

async function loadTimeMetric(metric) {

    const response = await fetch(
        `http://127.0.0.1:5000/api/time-metrics?metric=${metric}`
    );

    const data = await response.json();

    console.log("Time metric response:", data);

    const labels = data.map(d => {
        // formatting date to something more readable
        const date = new Date(d.trip_date);
        return date.toISOString().split("T")[0]; // YYYY-MM-DD date forkmat
    });

    const values = data.map(d => Number(d.value));

    renderLineGraph(labels, values, metric);
}


// On page load, load chart with most recent date's data and populate date dropdown
document.addEventListener("DOMContentLoaded", async () => {
    loadAvailableDates();
    loadTimeMetric("revenue");
});

// When user selects new date
document.getElementById("chartDatePicker").addEventListener("change", function() {
    loadTripsChart(this.value);
});
