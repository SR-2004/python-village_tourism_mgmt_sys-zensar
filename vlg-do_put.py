# # put method

import mysql.connector
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import date, datetime
from decimal import Decimal

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "sr@143",
    "database": "village_pro"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def convert_to_serializable(obj):
    """Convert non-serializable objects to serializable formats."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()  # Converts to 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SS'
    elif isinstance(obj, Decimal):
        return float(obj)  # Convert Decimal to float
    raise TypeError(f"Type {type(obj)} not serializable")

class RequestHandler(BaseHTTPRequestHandler):
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
                    query = """INSERT INTO customer_feedback (customer_id, feedback) VALUES (%s, %s)"""
                    cursor.execute(query, (customer_id, feedback))

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

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
    
    
# 
# # http://localhost:8080/customers/feedback
# {
#     "customer_id": 1,
#     "feedback": "Great experience hiking in the mountains!"
# } ..other info also u can provide as attraction_id and package_id