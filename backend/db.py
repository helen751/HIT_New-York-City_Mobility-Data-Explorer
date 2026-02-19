import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="HIT_team",
        password="StrongPass123!",    
        database="HIT_urban_mobility_db"
    )