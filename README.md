# Bank Management System

Student: Ramdev Kumar  
Registration Number: 26BAS10080

This is a small command-line bank management project made with Python and SQL. It stores customer details and supports SQLite and MySQL.

## What the program can do

- Login with one of the four sample users
- Add a customer
- Search for a customer by account number
- Show all customers
- Update a customer's name, birth year, IFSC or phone digits
- Delete a customer
- Use SQLite locally or connect to MySQL

## Requirements

- Python 3.8 or newer
- MySQL is optional
- `mysql-connector-python` is needed only when using MySQL

Install the package with:

```bash
python -m pip install -r requirements.txt
```

## Run with SQLite

SQLite is the easiest way to run the project because it does not need a MySQL server.

```bash
python Bank.py --db sqlite
```

The records are saved in `bank.db`.

## Run with MySQL

Create a `.env` file using `.env.example` and add your MySQL details:

```text
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=bank
```

Then run:

```bash
python Bank.py --db mysql
```

If `--db auto` is used, the program tries MySQL first and uses SQLite if MySQL is not available.

## Login details

The sample usernames and passwords are:

| Username | Password |
| --- | --- |
| Manager | Manager123 |
| Employee | Employee123 |
| Customer | Customer123 |
| Admin | Admin123 |

## Files

- `Bank.py` - main Python program
- `Bank.sql` - MySQL database setup
- `requirements.txt` - Python package used for MySQL
- `.env.example` - example MySQL settings
- `.gitignore` - files that should not be uploaded to Git
- `README.md` - project information

## Database table

The program uses a `customer` table with these columns:

- `customer_id` - account number
- `name` - customer name
- `YOB` - year of birth
- `IFSC` - branch IFSC code
- `phone_number` - last four digits of the phone number
