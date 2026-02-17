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
            AVG(trip_distance) as avg_distance,
            COUNT(*) as total_trips
        FROM trips
    """)

    result = cursor.fetchone()

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



