# # get method

# fetch village,attraction and location
import mysql.connector
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "sr@143",
    "database": "village_pro"
}

def get_db_connection():
    """Establish and return a database connection."""
    return mysql.connector.connect(**DB_CONFIG)

def fetch_village_and_attractions(village_id):
    """Fetch village and related attraction data based on village_id."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch the village data
        cursor.execute("SELECT * FROM villages WHERE village_id = %s", (village_id,))
        village = cursor.fetchone()

        if village:
            # Fetch related attractions
            cursor.execute("SELECT * FROM attractions WHERE village_id = %s", (village_id,))
            attractions = cursor.fetchall()

            # Display the data in a user-friendly manner
            print(f"\nVillage Name: {village['village_name']}")
            print(f"Location: {village['location']}")
            
            if attractions:
                print("\nAttractions:")
                for attraction in attractions:
                    print(f"- {attraction['attraction_name']} (Type: {attraction['attraction_type']})")
            else:
                print("No attractions available for this village.")

        else:
            print("No village found with the provided ID.")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            result = None

            # Fetch village data based on the village ID
            if self.path.startswith("/villages"):
                village_id = self.path.split("/")[-1]
                if village_id.isdigit():
                    cursor.execute("SELECT * FROM villages WHERE village_id = %s", (village_id,))
                    result = cursor.fetchone()

                    # If the village exists, fetch related attractions
                    if result:
                        cursor.execute("SELECT * FROM attractions WHERE village_id = %s", (village_id,))
                        attractions = cursor.fetchall()
                        
                        # Add the attractions to the village data
                        result["attractions"] = attractions

                        # Call the function to display the data
                        fetch_village_and_attractions(village_id)  # Automatically fetch and display

                else:
                    cursor.execute("SELECT * FROM villages")
                    result = cursor.fetchall()

            # Other logic for handling different routes can go here (e.g., /attractions)
            
        except Exception as e:
            print(f"Error: {str(e)}")
        finally:
            cursor.close()
            conn.close()

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()


