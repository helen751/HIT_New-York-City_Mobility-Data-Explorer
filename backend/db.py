import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",    
        database="HIT_urban_mobility_db"
    )