import mysql.connector
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import date, datetime

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "sr@143",
    "database": "village_pro"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

class RequestHandler(BaseHTTPRequestHandler):
    
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

# Function to run the server
def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()

