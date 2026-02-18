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
        SELECT 
            l.zone_name as zone,
            b.borough_name as borough,
            COUNT(*) AS trip_count
        FROM trips t
        JOIN locations l ON t.{column} = l.location_id
        JOIN boroughs b ON l.borough_id = b.borough_id
        GROUP BY t.{column}
        ORDER BY trip_count DESC
        LIMIT {limit}
    """

    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(result)

@app.route("/api/avg-fare-by-borough")
def avg_fare_by_borough():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            b.borough_name,
            s.avg_fare,
            s.trip_count,
            s.last_updated
        FROM borough_fare_summary s
        JOIN boroughs b 
            ON s.borough_id = b.borough_id
        ORDER BY s.avg_fare DESC
    """)

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(result)


@app.route("/api/filter")
def filter_trips():

    # Get query parameters from URL
    start = request.args.get("start")
    end = request.args.get("end")

    min_fare = request.args.get("min_fare", 0)
    max_fare = request.args.get("max_fare", 1000)

    passengers = request.args.get("passengers")
    min_distance = request.args.get("min_distance", 0)
    max_distance = request.args.get("max_distance", 1000)

    sort = request.args.get("sort", "pickup_datetime")

    # Whitelist allowed sorting columns (prevents SQL injection)
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

    query = """
        SELECT *
        FROM trips
        WHERE pickup_datetime BETWEEN %s AND %s
        AND fare_amount BETWEEN %s AND %s
        AND trip_distance BETWEEN %s AND %s
    """

    params = [start, end, min_fare, max_fare, min_distance, max_distance]

    # Optional passenger filter
    if passengers:
        query += " AND passenger_count = %s"
        params.append(passengers)

    query += f" ORDER BY {sort} LIMIT 500"

    cursor.execute(query, params)
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(data)

@app.route("/api/trips-over-time")
def trips_over_time():

    start = request.args.get("start")
    end = request.args.get("end")
    group = request.args.get("group", "hour")  # "hour" or "day"

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


@app.route("/api/peak-times")
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


if __name__ == "__main__":
    app.run(debug=True)



