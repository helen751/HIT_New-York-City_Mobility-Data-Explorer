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



