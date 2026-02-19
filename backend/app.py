from flask import Flask, request, jsonify
from flask_cors import CORS
from db import get_connection
from algorithm import quicksort

app = Flask(__name__)
CORS(app)


@app.route("/api/trips")
def get_trips():

    start = request.args.get("start")
    end = request.args.get("end")
    sort = request.args.get("sort", "pickup_datetime")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = f"""
        SELECT *
        FROM trips
        WHERE pickup_datetime BETWEEN %s AND %s
        ORDER BY {sort}
        LIMIT 500
    """

    cursor.execute(query, (start, end))
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(data)

@app.route("/api/available-dates")

# loading available dates for the date picker dropdown
def available_dates():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT DATE(pickup_datetime) as trip_date
        FROM trips
        ORDER BY trip_date DESC
    """)

    dates = [str(row[0]) for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return jsonify(dates)


@app.route("/api/summary")
def summary():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            AVG(fare_amount) as avg_fare,
            AVG(trip_distance) as avg_distance, AVG(avg_speed_mph) as avg_speed, SUM(total_amount) as avg_total_amount,
            COUNT(*) as total_trips
        FROM trips
    """)

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return jsonify(result)

@app.route("/api/top-locations")
def top_locations():

    loc_type = request.args.get("type", "pickup")
    limit = int(request.args.get("limit", 10))

    column = "pickup_location_id" if loc_type == "pickup" else "dropoff_location_id"

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = f"""
        SELECT l.zone_name as zone,
               b.borough_name as borough,
               summary.trip_count
        FROM (
            SELECT {column} AS location_id,
                   COUNT(*) AS trip_count
            FROM trips
            GROUP BY {column}
            ORDER BY trip_count DESC
            LIMIT %s
        ) AS summary
        JOIN locations l 
            ON summary.location_id = l.location_id
        JOIN boroughs b 
            ON l.borough_id = b.borough_id
        ORDER BY summary.trip_count DESC;
    """

    cursor.execute(query, (limit,))
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(result)

@app.route("/api/avg-fare-by-borough")
def avg_fare_by_borough():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT b.borough_name,
               summary.avg_fare,
               summary.trip_count
        FROM (
            SELECT l.borough_id,
                   AVG(t.fare_amount) AS avg_fare,
                   COUNT(*) AS trip_count
            FROM trips t
            JOIN locations l 
                ON t.pickup_location_id = l.location_id
            GROUP BY l.borough_id
        ) AS summary
        JOIN boroughs b 
            ON summary.borough_id = b.borough_id
        ORDER BY summary.avg_fare DESC;
    """)

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(result)


@app.route("/api/filter")

# filtering trips based on various parameters for the search section
def filter_trips():

    start = request.args.get("start")
    end = request.args.get("end")
    min_fare = request.args.get("min_fare")
    max_fare = request.args.get("max_fare")
    passengers = request.args.get("passengers")
    min_distance = request.args.get("min_distance")
    max_distance = request.args.get("max_distance")
    payment_type_id = request.args.get("payment_type_id")
    sort = request.args.get("sort", "pickup_datetime")

    allowed_sort = [
        "pickup_datetime",
        "fare_amount",
        "trip_distance",
        "passenger_count"
    ]

    if sort not in allowed_sort:
        sort = "pickup_datetime"

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM trips WHERE 1=1"
    params = []

    # Add filters only if they exist
    if start and end:
        query += " AND pickup_datetime BETWEEN %s AND %s"
        params.extend([start, end])

    if min_fare and max_fare:
        query += " AND fare_amount BETWEEN %s AND %s"
        params.extend([min_fare, max_fare])

    if min_distance and max_distance:
        query += " AND trip_distance BETWEEN %s AND %s"
        params.extend([min_distance, max_distance])

    if passengers:
        query += " AND passenger_count = %s"
        params.append(passengers)

    if payment_type_id:
        query += " AND payment_type_id = %s"
        params.append(payment_type_id)

    query += f" ORDER BY {sort} LIMIT 100"

    cursor.execute(query, params)
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(data)


@app.route("/api/trips-over-time")
def trips_over_time():

    start = request.args.get("start")
    end = request.args.get("end")
    group = request.args.get("group", "hour") 

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if group == "day":
        query = """
            SELECT 
                DATE(pickup_datetime) as time_label,
                COUNT(*) as trip_count
            FROM trips
            WHERE pickup_datetime BETWEEN %s AND %s
            GROUP BY DATE(pickup_datetime)
            ORDER BY time_label
        """
    else:
        query = """
            SELECT 
                HOUR(pickup_datetime) as time_label,
                COUNT(*) as trip_count
            FROM trips
            WHERE pickup_datetime BETWEEN %s AND %s
            GROUP BY HOUR(pickup_datetime)
            ORDER BY time_label
        """

    cursor.execute(query, (start, end))
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(data)


@app.route("/api/fare-distribution")
def fare_distribution():

    start = request.args.get("start")
    end = request.args.get("end")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            FLOOR(fare_amount / 5) * 5 AS fare_range,
            COUNT(*) AS trip_count
        FROM trips
        WHERE pickup_datetime BETWEEN %s AND %s
        GROUP BY fare_range
        ORDER BY fare_range
    """

    cursor.execute(query, (start, end))
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(data)


@app.route("/api/time-metrics")

# calculating metrics for total trips, revenue, and average fare over time for the line graph
def time_metrics():

    metric = request.args.get("metric", "trips")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if metric == "revenue":
        select_part = "SUM(total_amount) AS value"
    elif metric == "avg_fare":
        select_part = "AVG(fare_amount) AS value"
    else:
        select_part = "COUNT(*) AS value"

    query = f"""
        SELECT 
            DATE(pickup_datetime) AS trip_date,
            {select_part}
        FROM trips
        GROUP BY DATE(pickup_datetime)
        ORDER BY trip_date;
    """

    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(data)


@app.route("/api/peak-times")

# calculating peak hours and days based on total trip counts across all days
def peak_times():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Peak hour
    cursor.execute("""
        SELECT 
            HOUR(pickup_datetime) as peak_hour,
            COUNT(*) as trip_count
        FROM trips
        GROUP BY peak_hour
        ORDER BY trip_count DESC
        LIMIT 1
    """)

    peak_hour = cursor.fetchone()

    # Peak day
    cursor.execute("""
        SELECT 
            DATE(pickup_datetime) as peak_day,
            COUNT(*) as trip_count
        FROM trips
        GROUP BY peak_day
        ORDER BY trip_count DESC
        LIMIT 1
    """)

    peak_day = cursor.fetchone()

    cursor.close()
    conn.close()

    return jsonify({
        "peak_hour": peak_hour,
        "peak_day": peak_day
    })

@app.route("/api/busiest-weekday")

# calculating the busiest weekday based on average daily trips across the db
def busiest_weekday():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            weekday,
            AVG(daily_trip_count) AS avg_daily_trips
        FROM (
            SELECT 
                DAYOFWEEK(pickup_datetime) AS weekday_num,
                DAYNAME(pickup_datetime) AS weekday,
                COUNT(*) AS daily_trip_count
            FROM trips
            GROUP BY DATE(pickup_datetime), weekday_num, weekday
        ) AS daily_summary
        GROUP BY weekday_num, weekday
        ORDER BY avg_daily_trips DESC
        LIMIT 1;
    """)

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return jsonify(result)



@app.route("/api/top-expensive")
def top_expensive():

    k = int(request.args.get("k", 10))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT trip_id, fare_amount FROM trips LIMIT 1000")
    trips = cursor.fetchall()

    sorted_trips = quicksort(trips)

    cursor.close()
    conn.close()

    return jsonify(sorted_trips[:k])


@app.route("/api/payment-types")
def get_payment_types():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            payment_type_id,
            description
        FROM payment_types
        ORDER BY payment_type_id
    """)

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(result)



if __name__ == "__main__":
    app.run(debug=True)



