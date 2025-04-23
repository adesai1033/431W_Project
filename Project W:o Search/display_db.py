import sqlite3 as sql
from sqlite3 import Error
from tabulate import tabulate


def get_table_names(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [table[0] for table in cursor.fetchall()]


def display_table(cursor, table_name):
    # Get column names and types
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()
    column_names = [col[1] for col in columns_info]  # Just names for header
    column_types = [col[2] for col in columns_info]  # Just types for the second row

    # Get all data rows
    cursor.execute(f"SELECT * FROM {table_name}")
    data_rows = cursor.fetchall()

    # Combine the types row with the data rows
    rows_for_tabulate = list(data_rows) + [column_types]

    # Print table with tabulate
    print(f"\n=== {table_name} Table ===")
    print(tabulate(rows_for_tabulate, headers=column_names, tablefmt='grid'))
    # Adjust total rows count as we added the type row
    print(f"Total data rows: {len(data_rows)}\n")


def display_database():
    try:
        # Connect to the database
        connection = sql.connect('database.db')
        cursor = connection.cursor()

        # Get all table names
        tables = get_table_names(cursor)

        if not tables:
            print("No tables found in the database.")
            return

        while True:
            print("\nAvailable tables:")
            for i, table in enumerate(tables, 1):
                print(f"{i}. {table}")
            print("0. Exit")

            try:
                choice = int(input("\nEnter the number of the table to display (0 to exit): "))

                if choice == 0:
                    break
                elif 1 <= choice <= len(tables):
                    display_table(cursor, tables[choice - 1])
                else:
                    print("Invalid choice. Please try again.")

            except ValueError:
                print("Please enter a valid number.")

            # Ask if user wants to continue
            if choice != 0:
                cont = input("\nDo you want to view another table? (y/n): ").lower()
                if cont != 'y':
                    break

        connection.close()
        print("\nGoodbye!")

    except Error as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    display_database()