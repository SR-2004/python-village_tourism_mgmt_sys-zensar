# VILLAGE TOURISM MANAGEMENT SYSTEM ..PYTHON RESTFUL API
            
import mysql.connector
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import date, datetime

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "sr@143",
    "database": "village_pro"}

def get_db_connection():
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
            print("\nVillage Info :")
            print(f"\nVillage Id: {village['village_id']}")
            print(f"Village Name: {village['village_name']}")
            print(f"Location: {village['location']}")
            
            if attractions:
                print("\nAttraction Info :")
                for attraction in attractions:
                    print(f"Attraction name : {attraction['attraction_name']} (Type: {attraction['attraction_type']})")
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
    # fetch viilage,attraction and location
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

    # See booking confirmation and all info
    def do_POST(self):
        try:
            # Read and parse the data sent in the POST request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode("utf-8")
            request_data = json.loads(post_data)
            
            # Check if the request contains the action 'get_booking_status'
            if "action" in request_data and request_data["action"] == "get_booking_status":
                booking_id = request_data.get("booking_id")
                
                if booking_id:
                    # Fetch booking status for the given booking_id
                    result = self.get_booking_status(booking_id)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(result.encode())
                else:
                    self.send_error(400, "Bad Request: Missing booking_id")
            else:
                self.send_error(400, "Bad Request: Invalid action")
        
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def get_booking_status(self, booking_id):
        """ Fetch booking status based on booking_id """
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
            SELECT 
                c.first_name, 
                c.last_name, 
                b.booking_date, 
                b.start_date, 
                b.end_date, 
                p.package_name 
            FROM 
                bookings b
            JOIN 
                customers c ON b.customer_id = c.customer_id
            JOIN 
                tourism_packages p ON b.package_id = p.package_id
            WHERE 
                b.booking_id = %s
            """
            
            cursor.execute(query, (booking_id,))
            result = cursor.fetchone()
            
            if result:
                # Convert date objects to string using isoformat()
                result['booking_date'] = result['booking_date'].isoformat() if isinstance(result['booking_date'], (date, datetime)) else result['booking_date']
                result['start_date'] = result['start_date'].isoformat() if isinstance(result['start_date'], (date, datetime)) else result['start_date']
                result['end_date'] = result['end_date'].isoformat() if isinstance(result['end_date'], (date, datetime)) else result['end_date']
                
                return json.dumps(result, indent=4)
            else:
                return json.dumps({"error": "No booking found with the given booking_id"})
        
        except mysql.connector.Error as err:
            return json.dumps({"error": f"Error: {err}"})
        
        finally:
            cursor.close()
            conn.close()
            
    # give customers feedback on a specific thing like on attraction or package..else combine feedback
    def do_PUT(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            data = json.loads(put_data)

            if self.path.startswith("/customers/feedback"):
                # Allow customers to leave feedback
                customer_id = data.get('customer_id')
                feedback = data.get('feedback')
                attraction_id = data.get('attraction_id')  # Optional: Attraction ID
                package_id = data.get('package_id')  # Optional: Package ID
                
                if not customer_id or not feedback:
                    self.send_error(400, "Missing customer ID or feedback content")
                    return

                # If feedback is associated with either an attraction or a package, include that in the insert statement
                if attraction_id:
                    query = """INSERT INTO customer_feedback (customer_id, feedback, attraction_id) VALUES (%s, %s, %s)"""
                    cursor.execute(query, (customer_id, feedback, attraction_id))
                elif package_id:
                    query = """INSERT INTO customer_feedback (customer_id, feedback, package_id) VALUES (%s, %s, %s)"""
                    cursor.execute(query, (customer_id, feedback, package_id))
                else:
                    query = """INSERT INTO customer_feedback (customer_id, feedback,attraction_id,package_id) VALUES (%s,%s,%s, %s)"""
                    cursor.execute(query, (customer_id, feedback,attraction_id,package_id))

                conn.commit()

                self.send_response(201)
                self.end_headers()
                self.wfile.write(b"Feedback submitted successfully")

            else:
                self.send_error(404, "Endpoint not found")
                return

        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
        finally:
            cursor.close()
            conn.close()
            
    # delete or cancle booking and along with that delete automatically customers details too 
    def do_DELETE(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            if self.path.startswith("/bookings/"):
                booking_id = self.path.split("/")[-1]

                # Retrieve the booking and customer details before deletion
                cursor.execute("""
                    SELECT c.first_name, c.last_name, c.customer_id, p.package_name
                    FROM bookings b
                    JOIN customers c ON b.customer_id = c.customer_id
                    JOIN tourism_packages p ON b.package_id = p.package_id
                    WHERE b.booking_id = %s
                """, (booking_id,))
                result = cursor.fetchone()

                if not result:
                    self.send_error(404, "Booking not found")
                    return
                
                customer_name = f"{result[0]} {result[1]}"
                customer_id = result[2]
                package_name = result[3]

                # Delete the booking record
                cursor.execute("DELETE FROM bookings WHERE booking_id = %s", (booking_id,))

                # Delete the customer record only if the customer has no other bookings
                cursor.execute("""
                    SELECT COUNT(*) FROM bookings WHERE customer_id = %s
                """, (customer_id,))
                booking_count = cursor.fetchone()[0]

                if booking_count == 0:  # Only delete the customer if they have no other bookings
                    cursor.execute("DELETE FROM customers WHERE customer_id = %s", (customer_id,))

                # Commit changes
                conn.commit()

                # Display the message in a pretty format on the console
                print("\n" + "="*50)
                print(f"Booking Cancellation Successful\n")
                print(f"Customer: {customer_name}")
                print(f"Package Canceled: {package_name}")
                print(f"Booking ID: {booking_id}")
                print("\n" + "="*50)

            elif self.path.startswith("/villages/"):
                village_id = self.path.split("/")[-1]
                cursor.execute("DELETE FROM villages WHERE village_id = %s", (village_id,))
            elif self.path.startswith("/attractions/"):
                attraction_id = self.path.split("/")[-1]
                cursor.execute("DELETE FROM attractions WHERE attraction_id = %s", (attraction_id,))
            elif self.path.startswith("/tourism_packages/"):
                package_id = self.path.split("/")[-1]
                cursor.execute("DELETE FROM tourism_packages WHERE package_id = %s", (package_id,))
            elif self.path.startswith("/customers/"):
                customer_id = self.path.split("/")[-1]
                cursor.execute("DELETE FROM customers WHERE customer_id = %s", (customer_id,))
            else:
                self.send_error(404, "Endpoint not found")
                return

            self.send_response(202)
            self.end_headers()
            self.wfile.write(b"Record deleted successfully")

        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
        finally:
            cursor.close()
            conn.close()

# Function to run the server
def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()

    

# GET 
# Enter in postman as ... [ http://localhost:8080/villages/1 ] for do_get() method


# POST
# Enter in postman as ... [ http://localhost:8080/bookings ] for do_post() method
# {
#   "action": "get_booking_status",
#   "booking_id": 11
# }

# PUT
# Enter in postman as ... [ http://localhost:8080/customers/feedback ] for do_put() method
# {
#     "customer_id": 1,
#     "feedback": "Great experience!"
#  } ...give some feedback like this on postman in json file



# DELETE
# Enter in postman as ... [ http://localhost:8080/bookings/12 ] for do_delete() method
# on python console you will get output like this
# Booking Cancellation Successful

# Customer: Jane Smith
# Package Canceled: Romantic Getaway
# Booking ID: 12