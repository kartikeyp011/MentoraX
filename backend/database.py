import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE')
}

# Create connection pool
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mentorax_pool",
    pool_size=5,
    **db_config
)

def get_connection():
    """Get a connection from the pool"""
    return connection_pool.get_connection()

def execute_query(query, params=None, fetch=False):
    """Execute a query and optionally fetch results"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def fetch_one(query, params=None):
    """Fetch a single row"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        result = cursor.fetchone()
        return result
    finally:
        cursor.close()
        conn.close()

def fetch_all(query, params=None):
    """Fetch all rows"""
    return execute_query(query, params, fetch=True)

# Test connection on import
if __name__ == "__main__":
    try:
        conn = get_connection()
        print("✅ Database connection successful!")
        conn.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")