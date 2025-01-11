-- Tble creation and insertion

CREATE TABLE villages (
    village_id INT AUTO_INCREMENT PRIMARY KEY,
    village_name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    region VARCHAR(255),
    population INT
);

-- Insert 5 rows into `villages`
INSERT INTO villages (village_name, location, region, population) VALUES
('Karjat', 'Coastal Area', 'South Region', 5000),
('Alibaug', 'Coastal Area', 'West Region', 8000),
('Mahabaleshwar', 'Hill Area', 'North Region', 6000),
('Lonavala', 'Hill Area', 'West Region', 10000),
('Matheran', 'Hill Area', 'West Region', 7000);



CREATE TABLE attractions (
    attraction_id INT AUTO_INCREMENT PRIMARY KEY,
    village_id INT,
    attraction_name VARCHAR(255) NOT NULL,
    attraction_type VARCHAR(255),
    description TEXT,
    FOREIGN KEY (village_id) REFERENCES villages(village_id)
);

-- Insert 5 rows into `attractions`
INSERT INTO attractions (village_id, attraction_name, attraction_type, description) VALUES
(1, 'Nature Park', 'Recreational', 'A park with walking trails and picnic areas'),
(2, 'Beachside Fort', 'Historical', 'A historical fort near the beach with beautiful views'),
(3, 'Hilltop Viewpoint', 'Scenic', 'A stunning viewpoint with panoramic views of the valley'),
(4, 'Lake Lonavala', 'Nature', 'A serene lake surrounded by lush greenery'),
(5, 'Waterfall Trail', 'Adventure', 'A thrilling trek leading to a spectacular waterfall');




CREATE TABLE tourism_packages (
    package_id INT AUTO_INCREMENT PRIMARY KEY,
    package_name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2),
    duration INT,
    description TEXT
);

-- Insert 5 rows into `tourism_packages`
INSERT INTO tourism_packages (package_name, price, duration, description) VALUES
('Relaxation Pack', 800.00, 3, 'Perfect for a calm and restful getaway'),
('Family Pack', 1500.00, 7, 'Great for families, including kids-friendly attractions'),
('Adventure Pack', 2500.00, 5, 'An action-packed package for thrill-seekers'),
('Romantic Getaway', 2000.00, 4, 'Perfect for couples, featuring romantic locations'),
('Explorer Pack', 3000.00, 10, 'A thrilling pack for adventurers to explore various destinations');




CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone_number VARCHAR(20),
    address TEXT
);

-- Insert 5 rows into `customers`
INSERT INTO customers (first_name, last_name, email, phone_number, address) VALUES
('Siya', 'Sharma', 'siya123@gmail.com', '123-456-7890', '1234 alone Street, Cityville'),
('Johan', 'Shukla', 'johan@gmail.com', '123-555-7890', '5678 Oak Avenue, Townsville'),
('Alice', 'Johnson', 'alice.johnson@example.com', '123-666-7890', '91011 Pune Road, Villageburg'),
('Bob', 'Brown', 'bob12wn@gmail.com', '123-777-7890', '1213 Maple Lane, Hamlet'),
('Charlie', 'Davis', 'charlie.davis@gmail.com', '123-888-7890', '1415 Birch Bhopal, Countryside');




CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    package_id INT,
    booking_date DATE,
    start_date DATE,
    end_date DATE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (package_id) REFERENCES tourism_packages(package_id)
);

-- Insert 5 rows into `bookings`
INSERT INTO bookings (customer_id, package_id, booking_date, start_date, end_date) VALUES
(1, 3, '2025-01-15', '2025-02-01', '2025-02-05'),  
(2, 4, '2025-01-16', '2025-02-10', '2025-02-14'), 
(3, 5, '2025-01-17', '2025-02-20', '2025-03-01'),  
(4, 2, '2025-01-18', '2025-01-25', '2025-01-31'),  
(5, 1, '2025-01-19', '2025-02-05', '2025-02-07');  




CREATE TABLE customer_feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    feedback TEXT NOT NULL,
    feedback_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    attraction_id INT,  -- Optional, if feedback is specific to an attraction
    package_id INT,     -- Optional, if feedback is specific to a package
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (attraction_id) REFERENCES attractions(attraction_id),
    FOREIGN KEY (package_id) REFERENCES tourism_packages(package_id)
);


INSERT INTO customer_feedback (customer_id, feedback, attraction_id)
VALUES (1, 'Great experience hiking in the mountains!', 2);

INSERT INTO customer_feedback (customer_id, feedback, package_id)
VALUES (2, 'The beach package was amazing. Highly recommend!', 5);

