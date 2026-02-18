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

        await counterAnimation(); // Start the counter animation after updating the targets

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
        tableBody.innerHTML = ""; // Clear existing table rows

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
        tableBody.innerHTML = ""; // Clear existing table rows

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
        tableBody.innerHTML = ""; // Clear existing table rows

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
loadSummary();
loadTopPickups();
loadTopDrops();
loadAvgFareByBorough();