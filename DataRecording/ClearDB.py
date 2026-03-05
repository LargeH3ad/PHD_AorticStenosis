import sqlite3
import csv
from datetime import datetime

# Path to your database
db_file = "LiveData.db"

# Connect to database
conn = sqlite3.connect(r"C:\Users\pat\OneDrive - UNSW\ValveNN\PressureUltrasoundData.db")
cursor = conn.cursor()

try:
    # Ask for user confirmation
    confirm = input("WARNING: This will DELETE ALL DATA from the LiveData table. Type YES to continue: ")

    if confirm.strip().upper() == "YES":
        # --- Backup table to CSV ---
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_file = f"LiveData_backup_{timestamp_str}.csv"

        cursor.execute("SELECT * FROM LiveData;")
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]

        with open(backup_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(column_names)  # write headers
            writer.writerows(rows)         # write data

        print(f"Backup saved to {backup_file}")

        # --- Delete all rows ---
        cursor.execute("DELETE FROM LiveData;")
        conn.commit()
        print("All data cleared from LiveData table. Schema preserved.")

    else:
        print("Operation cancelled. No data was deleted.")

except Exception as e:
    print("Error:", e)

finally:
    conn.close()