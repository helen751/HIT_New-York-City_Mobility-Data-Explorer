// storing top pickup data for showing on the map
let map;
let markersLayer; 
let topPickupData = [];
let zoneLookup = {};

// writing the function to fetch summary data from the backend API and update the dashboard
async function loadSummary() {
    try {
        const response = await fetch("http://127.0.0.1:5000/api/summary");
        const data = await response.json();

        console.log("Summary:", data);
        const cardValues = document.getElementsByClassName('card-value');
        for (let i = 0; i < cardValues.length; i++) {
            cardValues[i].style.fontSize = '1.8rem'; // Setting bigger font size for all card values
        }

        // pupulating the summary data cards in the dashboard
       document.getElementById("totalTrips").textContent = data.total_trips;
        document.getElementById("avgFare").textContent = Number(data.avg_fare).toFixed(2);
        document.getElementById("avgDistance").textContent = Number(data.avg_distance).toFixed(2);
        document.getElementById("avgSpeed").textContent = Number(data.avg_speed).toFixed(2);
        document.getElementById("totalRevenue").textContent = Number(data.avg_total_amount).toFixed(2);

        await counterAnimation(); // Starting the counter animation after updating the targets

    } catch (error) {
        console.error("Error fetching summary:", error);
    }
}

// function to fetch the top 10 pickup locations and update the table
async function loadTopPickups() {
    try {
        const response = await fetch("http://127.0.0.1:5000/api/top-locations?type=pickup&limit=10");
        const data = await response.json();
        topPickupData = data;

        console.log("Top Pickups:", data);
        const tableBody = document.getElementById("topPickupsTable").getElementsByTagName('tbody')[0];
        tableBody.innerHTML = ""; // Clearing the existing table rows

        data.forEach((pickup) => {
            document.getElementById("topPickupsTable").getElementsByTagName('tbody')[0].innerHTML += `<tr><td>${pickup.zone}</td><td>${pickup.trip_count.toLocaleString()}</td></tr>`;
        });
        if (data.length === 0) {
            tableBody.innerHTML = "<tr><td colspan='2'>No Top Pickups Data Available</td></tr>";
        }   
    } catch (error) {
        console.error("Error fetching top pickups:", error);    
    }
}

// function to fetch the top 10 dropp off locations and update the table
async function loadTopDrops() {
    try {
        const response = await fetch("http://127.0.0.1:5000/api/top-locations?type=dropoff&limit=10");
        const data = await response.json();

        console.log("Top Drops:", data);
        const tableBody = document.getElementById("topDropsTable").getElementsByTagName('tbody')[0];
        tableBody.innerHTML = ""; // Clearing the existing table rows

        data.forEach((drop) => {
            document.getElementById("topDropsTable").getElementsByTagName('tbody')[0].innerHTML += `<tr><td>${drop.zone}</td><td>${drop.trip_count.toLocaleString()}</td></tr>`;
        });
        if (data.length === 0) {
            tableBody.innerHTML = "<tr><td colspan='2'>No Top Drop off Data Available</td></tr>";
        }   
    } catch (error) {
        console.error("Error fetching top drop offs:", error);    
    }
}

// function to fetch the average fare by borough and update the table
async function loadAvgFareByBorough() {
    try {
        const response = await fetch("http://127.0.0.1:5000/api/avg-fare-by-borough");
        const data = await response.json();

        console.log("Avg Fare by Borough:", data);
        const tableBody = document.getElementById("avgFareByBoroughTable").getElementsByTagName('tbody')[0];
        tableBody.innerHTML = ""; // Clearing the existing table rows

        data.forEach((borough) => {
            document.getElementById("avgFareByBoroughTable").getElementsByTagName('tbody')[0].innerHTML += `<tr><td>${borough.borough_name}</td><td>$${Number(borough.avg_fare).toFixed(2)}</td></tr>`;
        });
        if (data.length === 0) {
            tableBody.innerHTML = "<tr><td colspan='2'>No Average Fare by Borough Data Available</td></tr>";
        }   
    } catch (error) {
        console.error("Error fetching average fare by borough:", error);    
    }
}

// function to handle search logic and fetch filtered trips based on user input
document.getElementById("searchBtn").addEventListener("click", async function () {

    const method = document.getElementById("searchMethod").value;

    if (!method) {
        alert("Please select a search method.");
        return;
    }

    let queryParams = new URLSearchParams();

    // handling searching by date range
    if (method === "date") {
        const start = document.getElementById("startDate").value;
        const end = document.getElementById("endDate").value;

        if (!start) {
            alert("Please select the search start date.");
            return;
        }
        else if (!end) {
            alert("Please select the search end date.");
            return;
        }

        if (start > end) {
            alert("Your Start date cannot be after the end date.");
            return;
        }

        queryParams.append("start", start + " 00:00:00");
        queryParams.append("end", end + " 23:59:59");
    }

    // handling search by payment method
    if (method === "payment") {
        const payment = document.getElementById("paymentType").value;

        if (!payment) {
            alert("Please select a payment method.");
            return;
        }

        queryParams.append("payment_type_id", payment);
    }

    // Handling search by fare range
    if (method === "fare") {
        const minFare = document.getElementById("minFare").value;
        const maxFare = document.getElementById("maxFare").value;

        if (!minFare || !maxFare) {
            alert("Please enter both minimum and maximum fare.");
            return;
        }

        if (parseFloat(minFare) > parseFloat(maxFare)) {
            alert("Minimum fare cannot be greater than maximum fare.");
            return;
        }

        queryParams.append("min_fare", minFare);
        queryParams.append("max_fare", maxFare);
    }

    // Handling search by distance range
    if (method === "distance") {
        const minDistance = document.getElementById("minDistance").value;
        const maxDistance = document.getElementById("maxDistance").value;

        if (!minDistance || !maxDistance) {
            alert("Please enter both minimum and maximum distance.");
            return;
        }

        if (parseFloat(minDistance) > parseFloat(maxDistance)) {
            alert("Minimum distance cannot be greater than maximum distance.");
            return;
        }

        queryParams.append("min_distance", minDistance);
        queryParams.append("max_distance", maxDistance);
    }

    // Api call when all validations are passed and query parameters are set based on the search method selected by the user

    try {
        const response = await fetch(`http://127.0.0.1:5000/api/filter?${queryParams.toString()}`);

        if (!response.ok) {
            throw new Error("Error in the search request created. Please try again.");
        }

        const data = await response.json();

        console.log("Search Results:", data);

        if (data.length === 0) {
            alert("No results found for this search.");
        }
        else{
           renderResults(data);
        }

    } catch (error) {
        console.error("Search error:", error);
        alert("Something went wrong while searching.");
    }

});

// rendering the search results in a modal table
function renderResults(data) {

    const modal = document.getElementById("resultsModal");
    const tbody = document.querySelector("#resultsTable tbody");

    tbody.innerHTML = "";

    data.forEach(trip => {
        const row = `
            <tr>
                <td>${trip.trip_id}</td>
                <td>${trip.pickup_datetime}</td>
                <td>$${Number(trip.fare_amount).toFixed(2)}</td>
                <td>${Number(trip.trip_distance).toFixed(2)} mi</td>
                <td>${trip.passenger_count}</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });

    modal.classList.remove("hidden");
}

// Closing the search results modal
document.getElementById("closeModal").addEventListener("click", function () {
    document.getElementById("resultsModal").classList.add("hidden");
});

// Closing modal when clicking outside
window.addEventListener("click", function (event) {
    const modal = document.getElementById("resultsModal");
    if (event.target === modal) {
        modal.classList.add("hidden");
    }
});


async function loadInsights() {
    try {

        // getting the peak time from the api
        const peakResponse = await fetch("http://127.0.0.1:5000/api/peak-times");
        const peakData = await peakResponse.json();

        // Format peak hour from 24hr to 12hr
        const hour24 = peakData.peak_hour.peak_hour;
        const suffix = hour24 < 12 ? "AM" : "PM";
        let hour12 = hour24 % 12;
        hour12 = hour12 === 0 ? 12 : hour12;

        const formattedHour = `${hour12}:00 ${suffix}`;

        document.getElementById("peakHourText").textContent = formattedHour;

        document.getElementById("peakHourText").style.fontSize = '1.5rem';


        // Getting the busiest weekday from the api
        const weekdayResponse = await fetch("http://127.0.0.1:5000/api/busiest-weekday");
        const weekdayData = await weekdayResponse.json();

        document.getElementById("busiestDayText").textContent =
            weekdayData.weekday;
        document.getElementById("avgtrips").textContent =
            parseFloat(weekdayData.avg_daily_trips).toFixed(0).toLocaleString();

        // setting a bigger font size for the insights values
        document.getElementById("busiestDayText").style.fontSize = '1.5rem';

    } catch (error) {
        console.error("Error loading insights:", error);
        document.getElementById("peakHourText").textContent = "Unavailable";
        document.getElementById("busiestDayText").textContent = "Unavailable";
    }
}

// Load payment types into dropdown
async function loadPaymentTypes() {
    try {
        const response = await fetch("http://127.0.0.1:5000/api/payment-types");
        const data = await response.json();

        const select = document.getElementById("paymentType");
        select.innerHTML = '<option value="">Select Payment Method</option>';

        data.forEach(type => {
            const option = document.createElement("option");
            option.value = type.payment_type_id;
            option.textContent = type.description;
            select.appendChild(option);
        });

    } catch (error) {
        console.error("Error loading payment types:", error);
    }
}

// loading the full zone boundaries from the geojson file on the map using leaflet.js
async function loadGeoZones() {
    try {
        const response = await fetch("../../backend/processed/taxi_zones.geojson");
        const geoData = await response.json();

        // Build lookup dictionary for fast fetch
        geoData.features.forEach(feature => {
            const zoneName = feature.properties.zone;
            zoneLookup[zoneName] = feature;
        });

        console.log("Zone lookup ready:", zoneLookup);

    } catch (error) {
        console.error("Error loading geo zones:", error);
    }
}



// getting the top 10 pickup locations from the api and showing them as pins on the map

function renderTopPickupMarkers() {

    markersLayer.clearLayers();

    const bounds = [];

    topPickupData.forEach(top => {

        const feature = zoneLookup[top.zone];
        if (!feature) return;

        let coordinates;

        if (feature.geometry.type === "Polygon") {
            coordinates = feature.geometry.coordinates[0][0];
        } else {
            coordinates = feature.geometry.coordinates[0][0][0];
        }

        const lat = coordinates[1];
        const lng = coordinates[0];

        const marker = L.marker([lat, lng])
            .bindPopup(`
                <strong>${top.zone}</strong><br>
                Trips: ${top.trip_count.toLocaleString()}
            `);

        markersLayer.addLayer(marker);
        bounds.push([lat, lng]);
    });

    if (bounds.length > 0) {
        map.fitBounds(bounds, { padding: [50, 50] });
    }
}


// function to initialize the map and show location pins for top 10 pickup locations
function initMap() {

    map = L.map('map', {
        scrollWheelZoom: false
    }).setView([40.7128, -74.0060], 11);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // creating markers layer group to hold the location pins and adding it to the map
    markersLayer = L.layerGroup().addTo(map);
}





document.addEventListener("DOMContentLoaded", () => {

    // load everything on the dashboard when the page is loaded
    loadSummary();
    loadTopDrops();
    loadAvgFareByBorough();
    loadInsights();
    loadPaymentTypes();

    // Start loading geo and pickups in background
    Promise.all([
        loadTopPickups(),
        loadGeoZones()
    ]).then(() => {
        renderTopPickupMarkers();
    });

    setTimeout(() => {
        const overlay = document.getElementById("introOverlay");

        overlay.style.opacity = "0";

        setTimeout(() => {
            overlay.style.display = "none";
        }, 800);

    }, 9000); // animation duration 
});

