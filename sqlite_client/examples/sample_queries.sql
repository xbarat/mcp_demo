-- Sample SQL queries for SQLite MCP Client

-- Create a users table
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create an orders table
CREATE TABLE orders (
  id INTEGER PRIMARY KEY,
  user_id INTEGER,
  amount REAL NOT NULL,
  status TEXT,
  order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Insert sample users
INSERT INTO users (name, email) VALUES 
  ('John Doe', 'john@example.com'),
  ('Jane Smith', 'jane@example.com'),
  ('Bob Johnson', 'bob@example.com'),
  ('Alice Brown', 'alice@example.com'),
  ('Charlie Davis', 'charlie@example.com');

-- Insert sample orders
INSERT INTO orders (user_id, amount, status) VALUES 
  (1, 99.99, 'completed'),
  (1, 49.50, 'pending'),
  (2, 149.99, 'completed'),
  (3, 29.99, 'completed'),
  (4, 199.99, 'pending'),
  (2, 59.99, 'completed'),
  (5, 79.99, 'cancelled'),
  (3, 39.99, 'completed'),
  (4, 89.99, 'pending'),
  (5, 129.99, 'completed');

-- Sample SELECT queries

-- List all users
SELECT * FROM users;

-- List all orders
SELECT * FROM orders;

-- Join users and orders
SELECT u.name, o.amount, o.status, o.order_date
FROM users u
JOIN orders o ON u.id = o.user_id
ORDER BY o.order_date DESC;

-- Aggregate queries

-- Total orders by status
SELECT status, COUNT(*) as order_count, SUM(amount) as total_amount
FROM orders
GROUP BY status;

-- Top spending users
SELECT u.name, COUNT(o.id) as order_count, SUM(o.amount) as total_spent
FROM users u
JOIN orders o ON u.id = o.user_id
GROUP BY u.id
ORDER BY total_spent DESC;

-- Average order amount
SELECT AVG(amount) as average_order_amount FROM orders;

-- Business intelligence queries

-- Monthly sales trend
SELECT 
  strftime('%Y-%m', order_date) as month,
  COUNT(*) as order_count,
  SUM(amount) as monthly_revenue
FROM orders
GROUP BY month
ORDER BY month; 