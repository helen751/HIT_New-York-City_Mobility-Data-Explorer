import pandas as pd
import geopandas as gpd
import numpy as np
import os


# Paths to data files

TRIP_DATA_PATH = "backend/data/yellow_tripdata_2019-01.csv" 
ZONE_LOOKUP_PATH = "backend/data/taxi_zone_lookup.csv"
TAXI_ZONES_PATH = "backend/data/taxi_zones.zip"

os.makedirs("backend/processed", exist_ok=True)
os.makedirs("backend/logs", exist_ok=True)


# STEP 1: load datasets

def load_data():
    print("Loading datasets...")

    trips = pd.read_csv(TRIP_DATA_PATH)
    zone_lookup = pd.read_csv(ZONE_LOOKUP_PATH)

    # Load shapefile from zip
    taxi_zones = gpd.read_file(TAXI_ZONES_PATH)

    print("Datasets loaded successfully.")
    return trips, zone_lookup, taxi_zones



# STEP 2: Clean trip data

def clean_trips(trips):
    print("Cleaning trip data...")

    original_count = len(trips)

    # Convert datetime columns from strings to datetime objects, coercing errors to NaT

    trips["tpep_pickup_datetime"] = pd.to_datetime( trips["tpep_pickup_datetime"], errors="coerce")
    trips["tpep_dropoff_datetime"] = pd.to_datetime( trips["tpep_dropoff_datetime"], errors="coerce")

    trips = trips.dropna(subset=["tpep_pickup_datetime", "tpep_dropoff_datetime"])

    # Drop congestion_surcharge column 

    if "congestion_surcharge" in trips.columns:
        trips = trips.drop(columns=["congestion_surcharge"])

    trips = trips.drop_duplicates()

    # Calculating Trip duration (rounded to 2 decimals)

    trips["trip_duration_min"] = ( (trips["tpep_dropoff_datetime"] - trips["tpep_pickup_datetime"]) .dt.total_seconds() / 60).round(2)

    # Logical filters

    trips = trips[(trips["trip_duration_min"] > 0) & (trips["trip_duration_min"] < 600)]
    trips = trips[trips["trip_distance"] > 0]
    trips = trips[trips["fare_amount"] > 0]

    cleaned_count = len(trips)

    with open("backend/logs/cleaning_log.txt", "w") as f:
        f.write(f"Original: {original_count}\n")
        f.write(f"Cleaned: {cleaned_count}\n")
        f.write(f"Removed: {original_count - cleaned_count}\n")

    print("Trip cleaning completed.")
    return trips


# STEP 3: Feature engineering

def engineer_features(trips):
    print("Engineering features...")

    # Average speed (rounded to 2 decimals)
    trips["avg_speed_mph"] = np.where( trips["trip_duration_min"] > 0, (trips["trip_distance"] / (trips["trip_duration_min"] / 60)).round(2), 0)

    # Fare per mile (rounded to 2 decimals)
    trips["fare_per_mile"] = np.where( trips["trip_distance"] > 0, (trips["fare_amount"] / trips["trip_distance"]).round(2), 0)

    print("Feature engineering completed.")
    return trips


# STEP 4: Join with zone lookup to get borough and zone names

def integrate_lookup(trips, zone_lookup):
    print("Integrating zone lookup...")

    trips = trips.merge(
        zone_lookup,
        left_on="PULocationID",
        right_on="LocationID",
        how="left"
    ).rename(columns={
        "Borough": "PU_Borough",
        "Zone": "PU_Zone",
        "service_zone": "PU_ServiceZone"
    }).drop(columns=["LocationID"])

    trips = trips.merge(
        zone_lookup,
        left_on="DOLocationID",
        right_on="LocationID",
        how="left"
    ).rename(columns={
        "Borough": "DO_Borough",
        "Zone": "DO_Zone",
        "service_zone": "DO_ServiceZone"
    }).drop(columns=["LocationID"])

    trips["PU_Borough"] = trips["PU_Borough"].fillna("Unknown")
    trips["PU_Zone"] = trips["PU_Zone"].fillna("Unknown")
    trips["PU_ServiceZone"] = trips["PU_ServiceZone"].fillna("Unknown")

    trips["DO_Borough"] = trips["DO_Borough"].fillna("Unknown")
    trips["DO_Zone"] = trips["DO_Zone"].fillna("Unknown")
    trips["DO_ServiceZone"] = trips["DO_ServiceZone"].fillna("Unknown")


    print("Zone lookup integration done.")
    return trips


# STEP 5: Process spatial metadata 

def process_spatial_data(taxi_zones):
    print("Processing spatial metadata...")

    # Keep only relevant fields
    taxi_zones = taxi_zones[["LocationID", "borough", "zone", "geometry"]]

    # Ensure consistent CRS
    taxi_zones = taxi_zones.to_crs(epsg=4326)

    # Save as GeoJSON for frontend use
    taxi_zones.to_file("backend/processed/taxi_zones.geojson", driver="GeoJSON")

    print("Spatial data processed and exported.")
    return taxi_zones


# STEP 6: Save cleaned and enriched trip data

def save_output(trips):
    trips.to_csv("backend/processed/cleaned_trips.csv", index=False)
    print("Cleaned trips saved.")


# Main function to run the pipeline

def main():
    trips, zone_lookup, taxi_zones = load_data()

    trips = clean_trips(trips)

    trips = engineer_features(trips)

    trips = integrate_lookup(trips, zone_lookup)

    process_spatial_data(taxi_zones)

    save_output(trips)

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
