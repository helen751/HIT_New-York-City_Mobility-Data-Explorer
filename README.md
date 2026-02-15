# HIT_New-York-City_Mobility-Data-Explorer

# Database Schema

## ERD

 ![Database ERD](images/HIT_NYC_schema.drawio.png)
<a href="https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=HIT-NYC-schema.drawio&dark=auto#Uhttps%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D1mj2X9gLaWrXdCQXG60sgzsjAQdiXoT3-%26export%3Ddownload" target="_blank">View ERD on draw.io</a>

---

## Overview

This implementation loads the cleaned NYC taxi trip dataset into a structured MySQL relational database.

The loading script:

* Creates the database automatically if it does not exist
* Creates all required tables with constraints
* Applies primary keys, foreign keys, and a composite unique constraint on trips to identify a duplicate trip
* Loads relational tables first (vendors, rate codes, boroughs, service_zones, payment types and locations)
* Inserts trip records in optimized chunks (better memory usage)
* Prints progress updates while loading
* Handles all errors safely

---

## Important Requirement

Before loading the database, you **must run the cleaning pipeline first**:

```bash
python3 pipeline.py
```

This generates the cleaned dataset and stores under:

```
processed/cleaned_trips.csv
```

If the cleaned file is missing, the sql loader will stop safely and display:

```
Error: cleaned_trips.csv not found.
Run pipeline.py first to generate the cleaned CSV file.
```

---

## 🔐 Database Configuration

The loader script connects to MySQL using the following default credentials:

```python
host="localhost"
user="root"
password=""
database="HIT_urban_mobility_db"
```
- Make sure your MySQL server is running before executing the script.

## How To Load The Database

Once the cleaned CSV file exists, run:

```bash
python3 load_data_to_sql.py
```

That’s all.

The script will:

* Connect to MySQL
* Create the database (if needed)
* Create all tables
* Insert relational data
* Insert trips in batches
* Print progress while running
* Show a final summary with total records and execution time

---

## Example Output

Below is an example of what you will see while loading:

```
CSV file found. Loading data...
Database connection successful. Time started...

The data file is too large, we will load in chunks to optimize your computer memory
Now loading CSV data in chunks...

Scanning CSV in chunks completed under 25.40 seconds. Starting insert...

Relational tables populated under 0.11 seconds. Building locations...

All locations inserted in 0.02 seconds. Now inserting trips...

Inserted 10000 trips so far...
Inserted 20000 trips so far...
Inserted 30000 trips so far...
...
Inserted 7500000 trips so far...

Data successfully loaded into MySQL.

        Total number of trips inserted: 7571382
        Time used for Trip insertion: 365.54 seconds
        Total Time Used: 391.93 seconds
```

---

## Design Notes

* The database follows a normalized relational structure.
* All foreign keys are enforced.
* A composite unique constraint prevents duplicate trip entries.
* Data is inserted using `executemany()` for improved performance.
* Loading is done in chunks to prevent memory overload.
* Progress logs are printed so the user can monitor execution.
* Errors are handled safely, including missing files and connection issues.

---

## Full Setup Flow

To run everything from scratch:

```bash
python3 pipeline.py
python3 load_data_to_sql.py
```

After this, the database is fully populated and ready for querying and analysis.

