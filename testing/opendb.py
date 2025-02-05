import sqlite3

# Path to your .db file and output file
db_path = 'database.db'
output_file = 'database_contents.txt'

# Connect to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Open the output file in write mode
with open(output_file, 'w') as f:
    # Fetch and write the table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        f.write(f"Contents of table: {table_name}\n")
        
        # Get all rows from the table
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        for row in rows:
            f.write(f"{row}\n")
        f.write("\n" + "-"*50 + "\n")
    
# Close the connection
conn.close()

print(f"Database contents have been written to {output_file}")
