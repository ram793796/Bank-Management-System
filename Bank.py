"""
======================================================================
                   BANK MANAGEMENT SYSTEM
======================================================================
Student Name        : Ramdev Kumar
Registration Number : 26BAS10080
GitHub Username     : ram793796
GitHub Repository   : https://github.com/ram793796/Bank-Management-System
Project Description : Console-based banking database management system
                      supporting MySQL with automated SQLite fallback.
======================================================================
"""

import argparse
import os
import sqlite3
import sys

# Active database engine tracker and connection handles
active_engine = ''
db_conn = None
db_cursor = None

# SQL schema definition for the customer table
CREATE_CUSTOMER_TABLE_SQL = """CREATE TABLE IF NOT EXISTS customer (
    customer_id INT PRIMARY KEY,
    name VARCHAR(50),
    YOB VARCHAR(10),
    IFSC VARCHAR(20),
    phone_number INT
)"""

# System credentials for role-based access control
AUTHORIZED_USERS = {
    'Manager': 'Manager123',
    'Employee': 'Employee123',
    'Customer': 'Customer123',
    'Admin': 'Admin123'
}


# ---------------- Database Configuration & Connection ----------------

def load_environment_variables(env_filepath):
    """
    Parses configuration key-value pairs from a .env file
    and loads them into os.environ if not already defined.
    """
    if not os.path.exists(env_filepath):
        return
    
    with open(env_filepath, 'r', encoding='utf-8') as env_stream:
        for current_line in env_stream:
            current_line = current_line.strip()
            if not current_line or current_line.startswith('#') or '=' not in current_line:
                continue
            config_key, config_val = current_line.split('=', 1)
            config_key = config_key.strip()
            config_val = config_val.strip().strip('"').strip("'")
            if config_key not in os.environ:
                os.environ[config_key] = config_val


def create_mysql_connection():
    """
    Attempts to establish a connection to MySQL server and
    ensures the target database exists.
    """
    import mysql.connector as mysql_driver
    
    target_dbname = os.environ.get('DB_NAME', 'bank')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = int(os.environ.get('DB_PORT', '3306'))
    db_user = os.environ.get('DB_USER', 'root')
    db_pass = os.environ.get('DB_PASSWORD', '')

    mysql_conn = mysql_driver.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_pass
    )
    temp_cursor = mysql_conn.cursor()
    temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {target_dbname}")
    temp_cursor.execute(f"USE {target_dbname}")
    temp_cursor.close()
    return mysql_conn


def setup_database_engine(requested_engine, sqlite_filepath):
    """
    Initializes the database connection (MySQL or SQLite fallback)
    and verifies the customer table structure.
    """
    global active_engine, db_conn, db_cursor

    if requested_engine in ('mysql', 'auto'):
        try:
            db_conn = create_mysql_connection()
            active_engine = 'mysql'
        except ImportError:
            if requested_engine == 'mysql':
                print('[Error] MySQL driver not found. Install it with: pip install -r requirements.txt')
                sys.exit(1)
            print('[Info] mysql-connector-python not found. Falling back to SQLite.')
        except Exception as conn_err:
            if requested_engine == 'mysql':
                print(f'[Error] Could not connect to MySQL: {conn_err}')
                print('[Error] Verify DB_HOST, DB_USER, and DB_PASSWORD in your .env configuration.')
                sys.exit(1)
            print('[Info] MySQL server not accessible. Switching to local SQLite database.')

    if not active_engine:
        db_conn = sqlite3.connect(sqlite_filepath)
        active_engine = 'sqlite'

    if active_engine == 'mysql':
        # Buffered cursor retrieves all result rows immediately
        db_cursor = db_conn.cursor(buffered=True)
    else:
        db_cursor = db_conn.cursor()

    db_cursor.execute(CREATE_CUSTOMER_TABLE_SQL)
    db_conn.commit()

    if active_engine == 'mysql':
        active_db_name = os.environ.get('DB_NAME', 'bank')
        print(f"[Status] Active Database: MySQL -> {active_db_name}")
    else:
        print(f"[Status] Active Database: SQLite -> {sqlite_filepath}")


def execute_sql(statement, params=()):
    """
    Executes a SQL query, adapting query placeholders between SQLite (?) and MySQL (%s).
    """
    if active_engine == 'mysql':
        statement = statement.replace('?', '%s')
    db_cursor.execute(statement, params)
    return db_cursor


def terminate_session(exit_status=0):
    """
    Gracefully closes active database connection and terminates the program.
    """
    global db_conn
    if db_conn is not None:
        try:
            db_conn.close()
        except Exception:
            pass
    sys.exit(exit_status)


# ---------------- Input Validation Helpers ----------------

def prompt_input(display_message):
    """
    Prompts the user for console input, handling EOF gracefully.
    """
    try:
        return input(display_message)
    except EOFError:
        print("\n[Notice] No input stream detected. Terminating application.")
        terminate_session(0)


def prompt_integer(display_message):
    """
    Requests integer input from the user with validation.
    """
    while True:
        raw_val = prompt_input(display_message).strip()
        if raw_val.isdigit():
            return int(raw_val)
        print("[Validation Error] Only numeric digits are accepted. Please try again.")


def prompt_string(display_message):
    """
    Requests non-empty string input from the user.
    """
    while True:
        raw_text = prompt_input(display_message).strip()
        if raw_text:
            return raw_text
        print("[Validation Error] Input cannot be left blank. Please try again.")


def check_account_exists(acc_number):
    """
    Checks if a customer account with the given ID already exists in the database.
    """
    execute_sql("SELECT customer_id FROM customer WHERE customer_id = ?", (acc_number,))
    return db_cursor.fetchone() is not None


# ---------------- Table Output Formatting ----------------

def print_table_header():
    """Prints tabular column headers for customer records."""
    print(f"{'Account No':<14} {'Customer Name':<24} {'Birth Year':<12} {'IFSC Code':<16} {'Phone (Last 4)':<10}")
    print("-" * 78)


def print_record_row(record_data):
    """Prints a single customer record in formatted tabular structure."""
    print(f"{record_data[0]:<14} {record_data[1]:<24} {record_data[2]:<12} {record_data[3]:<16} {record_data[4]:<10}")


# ---------------- Banking Operation Handlers ----------------

def create_customer_record():
    print("\n" + "=" * 60)
    print("           INSERT NEW CUSTOMER RECORD WINDOW")
    print("=" * 60)
    
    add_another = 'yes'
    while add_another in ('yes', 'y', 'yep'):
        acc_id = prompt_integer("Enter Customer Account Number        : ")
        if check_account_exists(acc_id):
            print("[Alert] This account number already exists! Record was not saved.")
        else:
            cust_name = prompt_string("Enter Customer Full Name             : ")
            birth_year = prompt_string("Enter Customer Year of Birth (YYYY)  : ")
            branch_ifsc = prompt_string("Enter Branch IFSC Code               : ")
            contact_suffix = prompt_integer("Enter Last 4 Digits of Mobile Number : ")
            
            execute_sql(
                "INSERT INTO customer (customer_id, name, YOB, IFSC, phone_number) VALUES (?, ?, ?, ?, ?)",
                (acc_id, cust_name, birth_year, branch_ifsc, contact_suffix)
            )
            db_conn.commit()
            print("[Success] Customer record created successfully.")
            
        add_another = prompt_input("\nDo you want to add another record? (yes/no): ").strip().lower()


def search_customer_by_id():
    print("\n" + "=" * 60)
    print("            SEARCH CUSTOMER RECORD WINDOW")
    print("=" * 60)
    
    query_acc_id = prompt_integer("Enter Customer Account Number to Search: ")
    execute_sql("SELECT * FROM customer WHERE customer_id = ?", (query_acc_id,))
    matched_entry = db_cursor.fetchone()
    
    if matched_entry is not None:
        print("\n[Match Found] Customer Record Details:")
        print_table_header()
        print_record_row(matched_entry)
    else:
        print("[Notice] No customer found with that Account Number.")


def view_all_customers():
    print("\n" + "=" * 60)
    print("           DISPLAY ALL CUSTOMER RECORDS")
    print("=" * 60)
    
    execute_sql("SELECT * FROM customer ORDER BY customer_id ASC")
    all_customer_records = db_cursor.fetchall()
    
    record_count = len(all_customer_records)
    print(f"Total Customer Records Found: {record_count}\n")
    if record_count == 0:
        return
        
    print_table_header()
    for individual_record in all_customer_records:
        print_record_row(individual_record)


def modify_customer_record():
    print("\n" + "=" * 60)
    print("            UPDATE CUSTOMER RECORD WINDOW")
    print("=" * 60)
    
    target_id = prompt_integer("Enter Customer Account Number to Update: ")
    execute_sql("SELECT * FROM customer WHERE customer_id = ?", (target_id,))
    existing_entry = db_cursor.fetchone()
    
    if existing_entry is None:
        print("[Notice] Record not found for the given Account Number.")
        return
        
    print("\n[Current Record Details]")
    print_table_header()
    print_record_row(existing_entry)
    
    print("\nSelect Field to Update:")
    print("  1. Update Name")
    print("  2. Update Year of Birth")
    print("  3. Update Branch IFSC Code")
    print("  4. Update Mobile (Last 4 digits)")
    print("  5. Cancel")
    
    update_option = prompt_integer("Enter your choice (1-5): ")
    
    if update_option == 1:
        new_name = prompt_string("Enter updated customer name: ")
        execute_sql("UPDATE customer SET name = ? WHERE customer_id = ?", (new_name, target_id))
    elif update_option == 2:
        new_yob = prompt_string("Enter updated year of birth: ")
        execute_sql("UPDATE customer SET YOB = ? WHERE customer_id = ?", (new_yob, target_id))
    elif update_option == 3:
        new_ifsc = prompt_string("Enter updated IFSC code: ")
        execute_sql("UPDATE customer SET IFSC = ? WHERE customer_id = ?", (new_ifsc, target_id))
    elif update_option == 4:
        new_phone = prompt_integer("Enter updated last 4 digits of phone: ")
        execute_sql("UPDATE customer SET phone_number = ? WHERE customer_id = ?", (new_phone, target_id))
    elif update_option == 5:
        print("[Action Cancelled] No modifications made.")
        return
    else:
        print("[Error] Invalid selection. Operation cancelled.")
        return
        
    db_conn.commit()
    print("[Success] Customer record updated successfully.")


def remove_customer_record():
    print("\n" + "=" * 60)
    print("            DELETE CUSTOMER RECORD WINDOW")
    print("=" * 60)
    
    continue_deleting = 'yes'
    while continue_deleting in ('yes', 'y'):
        delete_id = prompt_integer("Enter Customer Account Number to Delete: ")
        if check_account_exists(delete_id):
            execute_sql("DELETE FROM customer WHERE customer_id = ?", (delete_id,))
            db_conn.commit()
            print(f"[Success] Record for Account #{delete_id} deleted successfully.")
        else:
            print(f"[Notice] No record found with Account Number {delete_id}.")
            
        continue_deleting = prompt_input("\nDo you want to delete another record? (yes/no): ").strip().lower()


def display_main_menu():
    while True:
        print("\n" + "=" * 50)
        print("             MAIN OPERATION MENU")
        print("=" * 50)
        print("  1. Insert New Customer Record")
        print("  2. Search Customer Record")
        print("  3. Display All Records")
        print("  4. Update Customer Record")
        print("  5. Delete Customer Record")
        print("  6. Exit System")
        print("=" * 50)
        
        selected_choice = prompt_integer("Enter your choice (1-6): ")
        
        if selected_choice == 1:
            create_customer_record()
        elif selected_choice == 2:
            search_customer_by_id()
        elif selected_choice == 3:
            view_all_customers()
        elif selected_choice == 4:
            modify_customer_record()
        elif selected_choice == 5:
            remove_customer_record()
        elif selected_choice == 6:
            print("\nThank you for using the Bank Management System. Have a great day!")
            break
        else:
            print("[Warning] Invalid selection. Please choose an option between 1 and 6.")


def verify_login_credentials():
    remaining_attempts = 3
    print("--------------------------------------------------")
    print("         SECURE USER LOGIN AUTHENTICATION")
    print("--------------------------------------------------")
    
    while remaining_attempts > 0:
        entered_user = prompt_input("Enter Username : ")
        entered_pass = prompt_input("Enter Password : ")
        
        # Check against AUTHORIZED_USERS with case-insensitive username match
        user_key = entered_user.strip()
        matched_user = None
        for registered_user in AUTHORIZED_USERS:
            if registered_user.lower() == user_key.lower():
                matched_user = registered_user
                break
                
        if matched_user and AUTHORIZED_USERS[matched_user] == entered_pass:
            print(f"\n[Login Successful] Welcome, {matched_user}!")
            return True
            
        remaining_attempts -= 1
        if remaining_attempts > 0:
            print(f"[Login Failed] Incorrect credentials. {remaining_attempts} attempt(s) remaining.\n")
            
    print("\n[Access Denied] Maximum authentication attempts exceeded. Exiting application.")
    return False


def main():
    cli_parser = argparse.ArgumentParser(
        description='Bank Management System - College Project by Ramdev Kumar (26BAS10080)'
    )
    cli_parser.add_argument('--db', choices=['auto', 'mysql', 'sqlite'], default='auto',
                            help='Database backend to use: auto, mysql, or sqlite (default: auto)')
    cli_parser.add_argument('--sqlite-file', default='bank.db',
                            help='File path for SQLite database (default: bank.db)')
    cli_parser.add_argument('--env-file', default='.env',
                            help='File path for environment configuration (default: .env)')
    cli_args = cli_parser.parse_args()

    load_environment_variables(cli_args.env_file)
    setup_database_engine(cli_args.db, cli_args.sqlite_file)

    print("\n" + "=" * 65)
    print("           WELCOME TO BANK MANAGEMENT SYSTEM")
    print("               Developed by: Ramdev Kumar")
    print("              Registration No: 26BAS10080")
    print("=" * 65)

    if verify_login_credentials():
        display_main_menu()
        
    terminate_session(0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[Stopped] Application execution interrupted by user.")
        terminate_session(0)
