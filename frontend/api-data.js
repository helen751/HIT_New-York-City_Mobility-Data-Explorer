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

        renderResults(data);

    } catch (error) {
        console.error("Search error:", error);
        alert("Something went wrong while searching.");
    }

});

loadSummary();
loadTopPickups();
loadTopDrops();
loadAvgFareByBorough();