# HIT New York City Mobility Data Explorer Backend API

This backend API provides endpoints to retrieve and filter trip data from the NYC mobility database. It is built using Flask and MySQL and is designed to support frontend visualization and analytics.

---

## Base URL

```
http://localhost:5000
```

---

# API Endpoints

## 1. Get Trips

Retrieves trip records within a specific date range.

### Endpoint

```
GET /api/trips
```

### The Date Range for the Database:

- **Start:** 2019-01-01
- **End:** 2019-02-01

### Example Request

```
http://localhost:5000/api/trips?start=2019-01-01&end=2019-02-01&sort=pickup_datetime
```

### Optional Parameters

| Parameter | Description |
|----------|-------------|
| start | Start date (YYYY-MM-DD) |
| end | End date (YYYY-MM-DD) |
| sort | Column to sort by (pickup_datetime, fare_amount, trip_distance) |

### Example Sorted by Fare

```
http://localhost:5000/api/trips?start=2019-01-01&end=2019-02-01&sort=fare_amount
```

---

## 2. Summary Statistics

Returns aggregated statistics for all trips.

### Endpoint

```
GET /api/summary
```

### Example Request

```
http://localhost:5000/api/summary
```

### Example Response

```json
{
    "avg_distance": "2.818954",
    "avg_fare": "12.244924",
    "total_trips": 7571382
}
```

---

## 3. Advanced Trip Filtering

Filters trips using date, fare, distance, and passenger count.

### Endpoint

```
GET /api/filter
```

### Example Request (Full Filter)

```
http://localhost:5000/api/filter?start=2019-01-01&end=2019-02-01&min_fare=5&max_fare=40&min_distance=1&max_distance=10&passengers=2&sort=fare_amount
```

### Parameters

| Parameter | Description |
|----------|-------------|
| start | Start date (YYYY-MM-DD) |
| end | End date (YYYY-MM-DD) |
| min_fare | Minimum fare amount |
| max_fare | Maximum fare amount |
| min_distance | Minimum trip distance |
| max_distance | Maximum trip distance |
| passengers | Passenger count |
| sort | Sorting column |

### What This Filter Does

The example above:

- Selects trips between Jan 1 and Feb 1, 2019
- Filters fares between 5 and 40
- Filters distances between 1 and 10 miles
- Only includes trips with 2 passengers
- Sorts by fare amount

---

# Running the Backend Server

## Step 1: Install Dependencies

```
pip install flask flask-cors mysql-connector-python
```

## Step 2: Start the Server

```
python app.py
```

## Step 3: Open in Browser

Visit:

```
http://localhost:5000/api/trips?start=2019-01-01&end=2019-02-01
```

---

# Notes

- Maximum 500 rows are returned per request for performance.
- All dates must be in **YYYY-MM-DD** format.
- Sorting is restricted to safe database columns.

---

---

