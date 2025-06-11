CREATE DATABASE zomato_assistant;
USE zomato;

CREATE TABLE restaurants (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  address TEXT,
  city VARCHAR(100),
  state VARCHAR(100),
  zipcode VARCHAR(20),
  cuisine VARCHAR(100),
  rating FLOAT,
  phone VARCHAR(50),
  opening_hours TEXT,
  avg_cost_for_two INT,
  image_url TEXT
);

CREATE TABLE tables (
  id INT AUTO_INCREMENT PRIMARY KEY,
  restaurant_id INT,
  table_number INT,
  capacity INT,
  is_available TINYINT DEFAULT 1,
  FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  email VARCHAR(255) UNIQUE,
  phone VARCHAR(50),
  password TEXT
);

CREATE TABLE bookings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  restaurant_id INT,
  table_id INT,
  customer_name VARCHAR(255),
  booking_time DATETIME,
  contact_number VARCHAR(50),
  num_people INT,
  status VARCHAR(50) DEFAULT 'booked',
  cancellation_reason TEXT,
  cancelled_at DATETIME,
  FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
  FOREIGN KEY (table_id) REFERENCES tables(id)
);

CREATE TABLE faqs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  restaurant_id INT,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);

CREATE TABLE menus (
  id INT AUTO_INCREMENT PRIMARY KEY,
  restaurant_id INT,
  item_name VARCHAR(255) NOT NULL,
  category VARCHAR(100),
  price FLOAT,
  description TEXT,
  availability TINYINT DEFAULT 1,
  FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);

CREATE TABLE orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  restaurant_id INT,
  customer_name VARCHAR(255),
  order_time DATETIME,
  total_amount FLOAT,
  status VARCHAR(50) DEFAULT 'pending',
  delivery_address TEXT,
  contact_number VARCHAR(50),
  cancellation_reason TEXT,
  cancelled_at DATETIME,
  FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);

CREATE TABLE order_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT,
  menu_item_id INT,
  quantity INT,
  item_price FLOAT,
  FOREIGN KEY (order_id) REFERENCES orders(id),
  FOREIGN KEY (menu_item_id) REFERENCES menus(id)
);

CREATE TABLE reviews (
  id INT AUTO_INCREMENT PRIMARY KEY,
  restaurant_id INT,
  customer_name VARCHAR(255),
  rating INT,
  comment TEXT,
  review_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);
