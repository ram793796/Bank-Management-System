import argparse
import os
import sqlite3

connection = None
cursor = None
using_mysql = False

users = {
    "Manager": "Manager123",
    "Employee": "Employee123",
    "Customer": "Customer123",
    "Admin": "Admin123"
}

create_table = """CREATE TABLE IF NOT EXISTS customer (
    customer_id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    YOB VARCHAR(10) NOT NULL,
    IFSC VARCHAR(20) NOT NULL,
    phone_number INT NOT NULL
)"""


def load_env(filename):
    if not os.path.isfile(filename):
        return

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key.strip(), value)


def mysql_connection():
    import mysql.connector

    db_name = os.environ.get("DB_NAME", "bank")
    db_host = os.environ.get("DB_HOST", "localhost")
    db_port = int(os.environ.get("DB_PORT", "3306"))
    db_user = os.environ.get("DB_USER", "root")
    db_password = os.environ.get("DB_PASSWORD", "")

    db = mysql.connector.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password
    )

    temp = db.cursor()
    temp.execute("CREATE DATABASE IF NOT EXISTS " + db_name)
    temp.execute("USE " + db_name)
    temp.close()
    return db


def start_database(choice, sqlite_file):
    global connection, cursor, using_mysql

    if choice in ("auto", "mysql"):
        try:
            connection = mysql_connection()
            using_mysql = True
            print("Using MySQL database.")
        except ImportError:
            if choice == "mysql":
                print("Please install mysql-connector-python first.")
                raise SystemExit(1)
            print("MySQL package not found. Using SQLite.")
        except Exception as error:
            if choice == "mysql":
                print("Could not connect to MySQL:", error)
                raise SystemExit(1)
            print("MySQL is not available. Using SQLite.")

    if connection is None:
        connection = sqlite3.connect(sqlite_file)
        using_mysql = False
        print("Using SQLite database:", sqlite_file)

    if using_mysql:
        cursor = connection.cursor(buffered=True)
    else:
        cursor = connection.cursor()

    cursor.execute(create_table)
    connection.commit()


def run_sql(query, values=()):
    if using_mysql:
        query = query.replace("?", "%s")
    cursor.execute(query, values)


def text_input(message):
    while True:
        value = input(message).strip()
        if value:
            return value
        print("This field cannot be empty.")


def number_input(message):
    while True:
        value = input(message).strip()
        if value.isdigit():
            return int(value)
        print("Please enter a number.")


def account_exists(account):
    run_sql("SELECT customer_id FROM customer WHERE customer_id = ?", (account,))
    return cursor.fetchone() is not None


def heading(text):
    print("\n" + "=" * 50)
    print(text)
    print("=" * 50)


def print_customer(customer):
    print("Account number:", customer[0])
    print("Name:", customer[1])
    print("Year of birth:", customer[2])
    print("IFSC:", customer[3])
    print("Phone (last 4 digits):", customer[4])


def add_customer():
    heading("ADD CUSTOMER")

    while True:
        account = number_input("Account number: ")

        if account_exists(account):
            print("This account number is already in use.")
        else:
            name = text_input("Name: ")
            yob = text_input("Year of birth: ")
            ifsc = text_input("IFSC code: ")
            phone = number_input("Last 4 digits of phone: ")

            run_sql(
                "INSERT INTO customer "
                "(customer_id, name, YOB, IFSC, phone_number) "
                "VALUES (?, ?, ?, ?, ?)",
                (account, name, yob, ifsc, phone)
            )
            connection.commit()
            print("Customer added.")

        answer = input("Add another customer? (y/n): ").strip().lower()
        if answer != "y":
            break


def search_customer():
    heading("SEARCH CUSTOMER")
    account = number_input("Account number: ")

    run_sql("SELECT * FROM customer WHERE customer_id = ?", (account,))
    customer = cursor.fetchone()

    if customer:
        print_customer(customer)
    else:
        print("Customer not found.")


def show_customers():
    heading("ALL CUSTOMERS")
    run_sql("SELECT * FROM customer ORDER BY customer_id")
    customers = cursor.fetchall()

    if not customers:
        print("No customer records found.")
        return

    for customer in customers:
        print("-" * 40)
        print_customer(customer)


def update_customer():
    heading("UPDATE CUSTOMER")
    account = number_input("Account number: ")

    run_sql("SELECT * FROM customer WHERE customer_id = ?", (account,))
    customer = cursor.fetchone()

    if not customer:
        print("Customer not found.")
        return

    print("Current information:")
    print_customer(customer)

    print("\n1. Change name")
    print("2. Change year of birth")
    print("3. Change IFSC")
    print("4. Change phone")
    print("5. Cancel")

    choice = number_input("Enter choice: ")

    if choice == 1:
        value = text_input("New name: ")
        run_sql("UPDATE customer SET name = ? WHERE customer_id = ?", (value, account))
    elif choice == 2:
        value = text_input("New year of birth: ")
        run_sql("UPDATE customer SET YOB = ? WHERE customer_id = ?", (value, account))
    elif choice == 3:
        value = text_input("New IFSC: ")
        run_sql("UPDATE customer SET IFSC = ? WHERE customer_id = ?", (value, account))
    elif choice == 4:
        value = number_input("New last 4 phone digits: ")
        run_sql("UPDATE customer SET phone_number = ? WHERE customer_id = ?", (value, account))
    elif choice == 5:
        print("No changes made.")
        return
    else:
        print("Invalid choice.")
        return

    connection.commit()
    print("Customer updated.")


def delete_customer():
    heading("DELETE CUSTOMER")

    while True:
        account = number_input("Account number: ")

        if account_exists(account):
            run_sql("DELETE FROM customer WHERE customer_id = ?", (account,))
            connection.commit()
            print("Customer deleted.")
        else:
            print("Customer not found.")

        answer = input("Delete another customer? (y/n): ").strip().lower()
        if answer != "y":
            break


def login():
    heading("LOGIN")

    for attempt in range(3):
        username = input("Username: ").strip()
        password = input("Password: ")

        found_user = None
        for user in users:
            if username.lower() == user.lower():
                found_user = user
                break

        if found_user and users[found_user] == password:
            print("Login successful. Welcome", found_user)
            return True

        print("Wrong username or password.")
        if attempt < 2:
            print("Try again.")

    print("Login failed three times.")
    return False


def menu():
    while True:
        heading("MAIN MENU")
        print("1. Add customer")
        print("2. Search customer")
        print("3. Show all customers")
        print("4. Update customer")
        print("5. Delete customer")
        print("6. Exit")

        choice = number_input("Enter choice: ")

        if choice == 1:
            add_customer()
        elif choice == 2:
            search_customer()
        elif choice == 3:
            show_customers()
        elif choice == 4:
            update_customer()
        elif choice == 5:
            delete_customer()
        elif choice == 6:
            print("Thank you for using the Bank Management System.")
            break
        else:
            print("Invalid choice. Enter 1 to 6.")


def main():
    parser = argparse.ArgumentParser(description="Bank Management System")
    parser.add_argument("--db", choices=["auto", "mysql", "sqlite"], default="auto")
    parser.add_argument("--sqlite-file", default="bank.db")
    parser.add_argument("--env-file", default=".env")
    args = parser.parse_args()

    load_env(args.env_file)
    start_database(args.db, args.sqlite_file)

    print("\nBank Management System")
    print("Student: Ramdev Kumar")
    print("Registration No: 26BAS10080")

    if login():
        menu()

    if connection:
        connection.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram stopped.")
