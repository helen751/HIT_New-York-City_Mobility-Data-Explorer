-- Active: 1769294247711@@127.0.0.1@3306@HIT_urban_mobility_db
# Create the database for the HIT Group Urban Mobility project
CREATE DATABASE IF NOT EXISTS HIT_urban_mobility_db 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Use the created database
USE `HIT_urban_mobility_db`;

# Setting the time zone to UTC for consistent timestamp across any devices and locations
SET TIME_ZONE = '+00:00';

# Setting the SQL mode to enforce strict data integrity and prevent invalid data from being inserted into the tables
SET sql_mode = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION';


# Creating the vendors table

CREATE TABLE IF NOT EXISTS vendors (
    vendor_id INT PRIMARY KEY COMMENT 'Storing the vendor ID which can have more entities in the future'
) ENGINE=InnoDB;

# Creating the boroughs table
CREATE TABLE IF NOT EXISTS boroughs (
    borough_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID for the boroughs',
    borough_name VARCHAR(50) UNIQUE NOT NULL COMMENT 'Storing the unique name of the boroughs in New York City'
) ENGINE=InnoDB;

# Creating the service zones table
CREATE TABLE IF NOT EXISTS service_zones (
    service_zone_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID for the service zones',
    service_zone_name VARCHAR(50) UNIQUE NOT NULL COMMENT 'Storing the unique name of the service zones in New York City'
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS locations (
    location_id INT PRIMARY KEY COMMENT 'Pick up LocationID / Drop off LocationID',
    zone_name VARCHAR(100) NOT NULL COMMENT 'Storing the name of the zone for the location',
    borough_id INT NOT NULL COMMENT 'Storing the borough ID for the location',
    service_zone_id INT NOT NULL COMMENT 'Storing the service zone ID for the location',

    -- Creating the foreign keys and Adding the ON DELETE and ON UPDATE actions to prevent deletes and update rule
    FOREIGN KEY (borough_id) REFERENCES boroughs(borough_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (service_zone_id) REFERENCES service_zones(service_zone_id) ON DELETE RESTRICT ON UPDATE CASCADE,

    -- Creating the borough index to optimize the joins
    INDEX idx_locations_borough (borough_id),
    INDEX idx_locations_service_zone (service_zone_id)
) ENGINE=InnoDB;

# Creating the payment types table
CREATE TABLE IF NOT EXISTS payment_types (
    payment_type_id INT PRIMARY KEY COMMENT 'ID for the payment types',
    description VARCHAR(50) COMMENT 'Storing the Payment type eg CARD'
) ENGINE=InnoDB;

# Stroing the rate codes
CREATE TABLE IF NOT EXISTS rate_codes (
    rate_code_id INT PRIMARY KEY COMMENT 'ID for the rate codes',
    description VARCHAR(100) COMMENT 'Storing the description of the rate code'
) ENGINE=InnoDB;

# Creating the trips table to link all the records together and store the trip data
CREATE TABLE IF NOT EXISTS trips (
    trip_id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID for each trip',

    vendor_id INT NOT NULL COMMENT 'Storing the vendor ID for the trip',
    pickup_datetime DATETIME NOT NULL COMMENT 'Storing the pickup date and time',
    dropoff_datetime DATETIME NOT NULL COMMENT 'Storing the dropoff date and time',

    passenger_count INT NOT NULL COMMENT 'Storing the number of passengers for the trip',
    trip_distance DECIMAL(6,2) NOT NULL COMMENT 'Storing the distance of the trip in miles',

    rate_code_id INT NOT NULL COMMENT 'Storing the rate code ID for the trip',
    store_and_fwd_flag CHAR(1) NOT NULL CHECK (store_and_fwd_flag IN ('Y','N')) COMMENT 'Storing the store and forward flag for the trip',

    pickup_location_id INT NOT NULL COMMENT 'Storing the pickup location ID for the trip',
    dropoff_location_id INT NOT NULL COMMENT 'Storing the dropoff location ID for the trip',

    payment_type_id INT NOT NULL COMMENT 'Storing the payment type ID for the trip',

    -- Storing the financial details of the trip
    fare_amount DECIMAL(8,2) NOT NULL,
    extra DECIMAL(6,2) NOT NULL DEFAULT 0,
    mta_tax DECIMAL(6,2) NOT NULL DEFAULT 0,
    tip_amount DECIMAL(8,2) NOT NULL DEFAULT 0,
    tolls_amount DECIMAL(8,2) NOT NULL DEFAULT 0,
    improvement_surcharge DECIMAL(6,2) NOT NULL DEFAULT 0,
    total_amount DECIMAL(8,2) NOT NULL,

    trip_duration_min DECIMAL(8,2) NOT NULL COMMENT 'Storing the duration of the trip in minutes',
    avg_speed_mph DECIMAL(6,2) NOT NULL COMMENT 'Storing the average speed of the trip in miles per hour',
    fare_per_mile DECIMAL(10,2) NOT NULL COMMENT 'Storing the fare per mile for the trip',

    -- Creating a unique trip
    UNIQUE KEY unique_trip (vendor_id, pickup_datetime, dropoff_datetime, pickup_location_id, dropoff_location_id),

    -- Creating the foreign keys and Adding the ON DELETE and ON UPDATE actions to prevent deletes and update rule
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (rate_code_id) REFERENCES rate_codes(rate_code_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (payment_type_id) REFERENCES payment_types(payment_type_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (pickup_location_id) REFERENCES locations(location_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (dropoff_location_id) REFERENCES locations(location_id) ON DELETE RESTRICT ON UPDATE CASCADE,

    -- Creating all the necessary indexes to optimize the queries on the trips table
    INDEX idx_trips_pickup_datetime (pickup_datetime),
    INDEX idx_trips_payment_type (payment_type_id),
    INDEX idx_trips_passenger (passenger_count),
    INDEX idx_trips_fare (fare_amount),
    INDEX idx_trips_trip_distance (trip_distance),

    -- composite indexes
    INDEX idx_trips_pickup_loc_tripid (pickup_location_id, fare_amount),
    INDEX idx_trips_dropoff_loc_tripid (dropoff_location_id, fare_amount)

) ENGINE=InnoDB;