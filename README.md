# Bank Management System

**Student Name:** Ramdev Kumar  
**Registration Number:** 26BAS10080  
**GitHub Profile:** [ram793796](https://github.com/ram793796)  
**GitHub Repository:** [Bank-Management-System](https://github.com/ram793796/Bank-Management-System)  
**Project:** College Python & SQL Database Project  

---

A command line application for storing and managing bank customer records. It is built using Python and MySQL. If MySQL is not available or not configured, the application automatically falls back to SQLite, allowing it to run seamlessly on any system.

The application runs directly in the terminal without requiring a graphical user interface.

## Features

* Role-based login authentication (`Manager`, `Employee`, `Customer`, `Admin`)
* Add new customer records with duplicate account number prevention
* Search customer records by account number
* Display all customer records in a clean tabular view
* Update specific fields (name, birth year, IFSC code, mobile number)
* Delete customer records with confirmation
* Full MySQL support with automatic SQLite fallback mode

## Requirements

* Python 3.8 or newer (tested on Python 3.13)
* MySQL Server 8.x — optional, only needed for MySQL mode
* `pip` for installing the required package

Check Python availability:

```bash
python --version
```

On Linux/macOS, you may need to use `python3` instead of `python`.

## Setup

### Step 1 - Clone the repository

```bash
git clone https://github.com/ram793796/Bank-Management-System.git
cd Bank-Management-System
```

### Step 2 — Create a virtual environment (optional)

```bash
python -m venv venv
```

Activate the environment:

```bash
# Windows (PowerShell or Command Prompt)
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
python -m pip install -r requirements.txt
```

This installs `mysql-connector-python`, required for connecting to MySQL. If omitted, the program runs in SQLite mode.

### Step 4 — Configure database connection (optional for MySQL)

Database connection settings can be configured via a `.env` file. Create it from `.env.example`:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Edit `.env` to configure your MySQL connection:

```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=bank
```

### Step 5 — Initialize MySQL database (optional)

```bash
mysql -u root -p < Bank.sql
```

This creates the `bank` database and `customer` table. The application will also automatically create them on startup if missing.

### Step 6 — Run the program

```bash
python Bank.py
```

## Running with SQLite (No MySQL required)

To run the program entirely in SQLite mode:

```bash
python Bank.py --db sqlite
```

Records will be stored in `bank.db` in the project directory.

When launched with `python Bank.py`, the program attempts to connect to MySQL first and automatically defaults to SQLite if MySQL is unreachable.

## Command Line Options

| Option | Description | Default |
| --- | --- | --- |
| `--db {auto,mysql,sqlite}` | Database backend. `auto` tests MySQL and falls back to SQLite. | `auto` |
| `--sqlite-file PATH` | SQLite database file location. | `bank.db` |
| `--env-file PATH` | Configuration file containing database credentials. | `.env` |
| `-h`, `--help` | Show command line help message and exit. | — |

## Login Details

The application prompts for login credentials prior to opening the main operations menu (maximum 3 attempts). Default accounts:

| Role / Username | Password |
| --- | --- |
| `Manager` | `Manager123` |
| `Employee` | `Employee123` |
| `Customer` | `Customer123` |
| `Admin` | `Admin123` |

## Example Session

```
$ python Bank.py --db sqlite
[Status] Active Database: SQLite -> bank.db

=================================================================
           WELCOME TO BANK MANAGEMENT SYSTEM
               Developed by: Ramdev Kumar
              Registration No: 26BAS10080
=================================================================
--------------------------------------------------
         SECURE USER LOGIN AUTHENTICATION
--------------------------------------------------
Enter Username : Manager
Enter Password : Manager123

[Login Successful] Welcome, Manager!

==================================================
             MAIN OPERATION MENU
==================================================
  1. Insert New Customer Record
  2. Search Customer Record
  3. Display All Records
  4. Update Customer Record
  5. Delete Customer Record
  6. Exit System
==================================================
Enter your choice (1-6): 1

============================================================
           INSERT NEW CUSTOMER RECORD WINDOW
============================================================
Enter Customer Account Number        : 1001
Enter Customer Full Name             : Ramdev Kumar
Enter Customer Year of Birth (YYYY)  : 2004
Enter Branch IFSC Code               : SBIN0004567
Enter Last 4 Digits of Mobile Number : 7890
[Success] Customer record created successfully.

Do you want to add another record? (yes/no): no

==================================================
             MAIN OPERATION MENU
==================================================
Enter your choice (1-6): 3

============================================================
           DISPLAY ALL CUSTOMER RECORDS
============================================================
Total Customer Records Found: 1

Account No     Customer Name            Birth Year   IFSC Code        Phone (Last 4)
------------------------------------------------------------------------------
1001           Ramdev Kumar             2004         SBIN0004567      7890

==================================================
             MAIN OPERATION MENU
==================================================
Enter your choice (1-6): 6

Thank you for using the Bank Management System. Have a great day!
```

## Database Schema

Table `customer`:

| Column | Type | Description |
| --- | --- | --- |
| `customer_id` | `INT PRIMARY KEY` | Customer account number (unique identifier) |
| `name` | `VARCHAR(50)` | Full name of the customer |
| `YOB` | `VARCHAR(10)` | Year of birth |
| `IFSC` | `VARCHAR(20)` | Branch IFSC code |
| `phone_number` | `INT` | Last 4 digits of customer's mobile number |

## Project Structure

* `Bank.py` — Core application logic, database interface, and console UI
* `Bank.sql` — MySQL database creation and schema setup script
* `requirements.txt` — Project dependencies (`mysql-connector-python`)
* `.env.example` — Environment configuration template
* `.gitignore` — Git exclusion rules
* `README.md` — Project documentation and setup guide

## Troubleshooting

* **MySQL Connection Refused / Error 2003:** MySQL service is not running or port is incorrect. Run SQLite mode instead: `python Bank.py --db sqlite`.
* **Access Denied / Error 1045:** Check `DB_USER` and `DB_PASSWORD` in your `.env` file.
* **MySQL Connector Missing:** Run `python -m pip install -r requirements.txt`.
* **Digits validation error:** Account number, phone digits, and menu selections accept numbers only.
