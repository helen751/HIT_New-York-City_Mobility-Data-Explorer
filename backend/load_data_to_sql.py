import os
import sys
import pandas as pd
import mysql.connector
import time

# defining the database connecton function
def connect_to_db():
    # Database connection enclosed in try and catch to handle potential connection errors
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="HIT_team",
            password="StrongPass123!",
            database="HIT_urban_mobility_db" # our db name
        )
        return conn
    except mysql.connector.Error as err:

        # checking if the error is database does not exist
        if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist. Run the database_setup.sql script first to create the database and tables.\n")
            sys.exit(1)

        else:
            print("Database connection failed:", err)
            sys.exit(1)

# load the cleaned CSV file and check if it exists
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "processed", "cleaned_trips.csv")

if not os.path.exists(file_path):
    print("Error: cleaned_trips.csv not found. Run the pipeline.py first to generate the cleaned CSV file.\n")
    sys.exit(1)

print("CSV file found. Loading data...")

# Calling the database connection function
conn = connect_to_db()
cursor = conn.cursor()

print("Database connection successful. Time started...\n")

overall_start = time.time()

# Reading the CSV file into a pandas DataFrame
print("The data file is too large, we will load in chunks to optimize your computer memory")
print("Now loading CSV data in chunks...\n")

chunk_size = 10000
vendors = set()
payment_types = set()
rate_codes = set()
boroughs = set()
zones = set()

# collecting unique locations first (in memory)
unique_locations = {}

for chunk in pd.read_csv(file_path, chunksize=chunk_size):

    # collecting the unique vendor IDs, payment types, rate codes, boroughs, and zones from the chunk to insert into relational tables
    vendors.update(chunk["VendorID"].unique())
    payment_types.update(chunk["payment_type"].unique())
    rate_codes.update(chunk["RatecodeID"].unique())

    boroughs.update(chunk["PU_Borough"].unique())
    boroughs.update(chunk["DO_Borough"].unique())

    zones.update(chunk["PU_ServiceZone"].unique())
    zones.update(chunk["DO_ServiceZone"].unique())

    # Collecting unique locations from the chunk and storing them in a dictionary
    for row in chunk.itertuples(index=False):

        unique_locations[row.PULocationID] = (
            row.PU_Zone,
            row.PU_Borough,
            row.PU_ServiceZone
        )

        unique_locations[row.DOLocationID] = (
            row.DO_Zone,
            row.DO_Borough,
            row.DO_ServiceZone
        )
print(f"Scanning CSV in chunks completed under {time.time() - overall_start:.2f} seconds. Starting insert...\n")

# building descriptions for rate codes, since it is not given in the CSV
rate_mapping = {
    1: "Standard rate",
    2: "JFK airport flat fare",
    3: "Newark airport flat fare",
    4: "Nassau or Westchester fare",
    5: "Negotiated fare",
    6: "Group ride"
}

# building descriptions for payment types, since it is not given in the CSV
payment_mapping = {
    1: "Credit card",
    2: "Cash",
    3: "No charge",
    4: "Dispute",
    5: "Unknown",
    6: "Voided trip"
}

# Handling unexpected ID values that are not in the mapping (if any)
for pt in payment_types:
    if pt not in payment_mapping:
        payment_mapping[pt] = "Other"

for rate in rate_codes:
    if rate not in rate_mapping:
        rate_mapping[rate] = "Other"


# ==== Starting the insertion process ====
start_time = time.time()

# Inserting to vendors table first
vendor_values = [(int(v),) for v in vendors]
cursor.executemany(
    "INSERT IGNORE INTO vendors (vendor_id) VALUES (%s)",
    vendor_values
)

# Inserting to payment_types table
payment_type_values = [(int(pt), payment_mapping[pt]) for pt in payment_types]
cursor.executemany(
    "INSERT IGNORE INTO payment_types (payment_type_id, description) VALUES (%s, %s)",
    payment_type_values
)

# Inserting to rate_codes table
rate_code_values = [(int(rate), rate_mapping[rate]) for rate in rate_codes]
cursor.executemany(
    "INSERT IGNORE INTO rate_codes (rate_code_id, description) VALUES (%s, %s)",
    rate_code_values
)

borough_values = [(borough,) for borough in boroughs]
cursor.executemany(
    "INSERT IGNORE INTO boroughs (borough_name) VALUES (%s)",
    borough_values
)

zone_values = [(zone,) for zone in zones]
cursor.executemany(
    "INSERT IGNORE INTO service_zones (service_zone_name) VALUES (%s)",
    zone_values
)
# running the commit first, before inserting into trips and locations for foreign key dependencies
conn.commit()

print(f"Relational tables populated under {time.time() - start_time:.2f} seconds. Building locations...\n")

# starting the timer for location insertion
start_time = time.time()

# building a dictionary to map location and optimize for O(1) lookups
cursor.execute("SELECT borough_id, borough_name FROM boroughs")
borough_map = {name: id for id, name in cursor.fetchall()}

cursor.execute("SELECT service_zone_id, service_zone_name FROM service_zones")
zone_map = {name: id for id, name in cursor.fetchall()}

location_values = []

# Inserting locations at once to optimize for speed
for location_id, (zone_name, borough_name, service_zone_name) in unique_locations.items():

    location_values.append((
        location_id,
        zone_name,
        borough_map[borough_name],
        zone_map[service_zone_name]
    ))

cursor.executemany(
    "INSERT IGNORE INTO locations (location_id, zone_name, borough_id, service_zone_id) VALUES (%s, %s, %s, %s)",
    location_values
)

conn.commit()

print(f"All locations inserted in {time.time() - start_time:.2f} seconds. Now inserting trips...\n")
del unique_locations # clearing the unique_locations dictionary from memory since it is no longer needed

# Starting the timer for trip insertion
start_time = time.time()
chunk_size = 10000
rows_inserted = 0
chunk_counter = 0
commit_every = 5 # commit after every 5 chunks to manage memory and speed up inserting

# Inserting into trips table with all foreign keys already in place
query = "INSERT IGNORE INTO trips (vendor_id, pickup_datetime, dropoff_datetime, passenger_count, trip_distance, rate_code_id, store_and_fwd_flag, pickup_location_id, dropoff_location_id, payment_type_id, fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount, trip_duration_min, avg_speed_mph, fare_per_mile) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"


# iterating through the DataFrame and inserting each trip record into the trips table in chunks

for chunk in pd.read_csv(file_path, chunksize=chunk_size): 

    trip_values = []

    for each_trip in chunk.itertuples(index=False):
        trip_values.append((
            each_trip.VendorID,
            each_trip.tpep_pickup_datetime,
            each_trip.tpep_dropoff_datetime,
            each_trip.passenger_count,
            each_trip.trip_distance,
            each_trip.RatecodeID,
            each_trip.store_and_fwd_flag,
            each_trip.PULocationID,
            each_trip.DOLocationID,
            each_trip.payment_type,
            each_trip.fare_amount,
            each_trip.extra,
            each_trip.mta_tax,
            each_trip.tip_amount,
            each_trip.tolls_amount,
            each_trip.improvement_surcharge,
            each_trip.total_amount,
            each_trip.trip_duration_min,
            each_trip.avg_speed_mph,
            each_trip.fare_per_mile
        ))

    cursor.executemany(query, trip_values)
    
    chunk_counter += 1
    if chunk_counter % commit_every == 0:
        conn.commit()

    rows_inserted += len(trip_values)
    print(f"Inserted {rows_inserted} trips so far...")

conn.commit() # final commit for any remaining records

print("Trips inserted successfully, counting the number of records...\n")
trip_time = time.time() - start_time

cursor.execute("SELECT COUNT(*) FROM trips")
trip_count = cursor.fetchone()[0]

# Final output summary of the operation results
print("Data successfully loaded into MySQL.\n\n")
print(f"\tTotal number of trips inserted: {trip_count}")
print("\tTime used for Trip insertion:", round(trip_time, 2), "seconds")
print("\tTotal Time Used:", round(time.time() - overall_start, 2), "seconds\n\n")

# closing the database connection
cursor.close()
conn.close() 
