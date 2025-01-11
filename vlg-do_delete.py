# cancel booking ..whenever customer will cancel the booking automatically its name or biodata will also get canceled from customers table

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

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
