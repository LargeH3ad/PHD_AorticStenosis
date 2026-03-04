import sqlite3

conn = sqlite3.connect(r"C:\Users\pat\OneDrive - UNSW\ValveNN\SQL_Database.db")
cursor = conn.cursor()

while True:
    choice = input("A = add, U = update, D = delete, L = list")
    if choice == "A":
        name = input("Name: \n")
        value = input("Value: \n")

        data = [name, value]
        cursor.execute("INSERT INTO 'TestDB' ('name', 'value') VALUES (?, ?)", data)
        conn.commit()

    if choice == "U":
        name = input("ID: \n")
        value = input("New value: \n")
        
        data = [name, value]
        cursor.execute("UPDATE 'TestDB' SET 'value' = ? WHERE 'name' = ?", (value, name))
        conn.commit()
    
    if choice == "D":
        name = input("ID to delete: \n")
        cursor.execute("DELETE FROM 'TestDB' WHERE 'name' = ?", (name,))
        conn.commit()
        
        data = [name, value]
        cursor.execute("INSERT INTO 'TestDB' ('name', 'value') VALUES (?, ?)", data)
        conn.commit()
    
    if choice == "L":
        cursor.execute("SELECT * FROM 'TestDB'")
        records = cursor.fetchall()
        for record in records:
            print(record)
    
    else:
        break

