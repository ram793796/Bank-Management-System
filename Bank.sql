-- ===============================================================
-- Bank Management System : MySQL Database Schema
-- Student Name        : Ramdev Kumar
-- Registration Number : 26BAS10080
-- GitHub Username     : ram793796
-- GitHub Repository   : https://github.com/ram793796/Bank-Management-System
-- Project             : College Python & SQL Project
-- ===============================================================
--
-- Instructions:
-- Execute this script once to initialize the MySQL database and table:
--     mysql -u root -p < Bank.sql
--
-- Note: The Python application also automatically creates the database
-- and table if they do not already exist.

CREATE DATABASE IF NOT EXISTS bank;
USE bank;

CREATE TABLE IF NOT EXISTS customer (
    customer_id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    YOB VARCHAR(10) NOT NULL,
    IFSC VARCHAR(20) NOT NULL,
    phone_number INT NOT NULL
);

-- Optional sample record for demonstration
-- INSERT INTO customer (customer_id, name, YOB, IFSC, phone_number)
-- VALUES (1001, 'Ramdev Kumar', '2004', 'SBIN0004567', 7890);
