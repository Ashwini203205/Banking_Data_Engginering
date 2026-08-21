CREATE SCHEMA IF NOT EXISTS bronze; 
CREATE SCHEMA IF NOT EXISTS silver; 
CREATE SCHEMA IF NOT EXISTS gold; 
CREATE TABLE IF NOT EXISTS bronze.customer_raw (age INT, job VARCHAR(50), marital VARCHAR(50), education VARCHAR(50), default_status VARCHAR(10), balance INT, housing VARCHAR(10), loan VARCHAR(10), contact VARCHAR(50), day INT, month VARCHAR(20), duration INT, campaign INT, pdays INT, previous INT, poutcome VARCHAR(50), y VARCHAR(10)); CREATE TABLE IF NOT EXISTS silver.customer_clean (LIKE bronze.customer_raw INCLUDING ALL); CREATE TABLE IF NOT EXISTS gold.customer_summary (total_customers INT, subscribed_customers INT, average_age NUMERIC, average_balance NUMERIC, total_balance BIGINT);
