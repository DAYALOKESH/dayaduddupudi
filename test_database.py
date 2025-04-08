import psycopg2
import sys

def test_database_connectivity():
    print("Testing database connectivity...")
    try:
        conn = psycopg2.connect(
            dbname="road_network",
            user="postgres",
            password="mysecretpassword",
            host="localhost"
        )
        cursor = conn.cursor()
        
        # Check which tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public'
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Found tables: {', '.join(tables)}")
        
        # If ways table exists, count records
        if 'ways' in tables:
            cursor.execute("SELECT COUNT(*) FROM ways")
            count = cursor.fetchone()[0]
            print(f"Number of records in ways table: {count}")
        
        # If road_segments table exists, count records
        if 'road_segments' in tables:
            cursor.execute("SELECT COUNT(*) FROM road_segments")
            count = cursor.fetchone()[0]
            print(f"Number of records in road_segments table: {count}")
        
        conn.close()
        print("Database connectivity test passed!")
        return True
    except Exception as e:
        print(f"Database connectivity test failed: {str(e)}")
        return False

if __name__ == "__main__":
    if not test_database_connectivity():
        sys.exit(1)
