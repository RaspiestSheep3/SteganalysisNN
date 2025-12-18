import sqlite3
import ast

database = r"SteganalysisNNTrainingDatabaseBPCS.db"

# Read CSV lines
with open(r"DataOverviewBPCS.csv", "r") as fileHandle:
    linesRaw = fileHandle.readlines()

lines = []
for line in linesRaw:
    # Wrap line in brackets so it's a list of lists and safely evaluate
    lines.append(ast.literal_eval(f"[{line.strip()}]"))

print(f"Total lines: {len(lines)}")

# Connect to DB
conn = sqlite3.connect(database)
cursor = conn.cursor()

cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS files (
        rawNum INTEGER NOT NULL,
        versionNum INTEGER NOT NULL,
        embedPercentage FLOAT NOT NULL,
        cutoff FLOAT NOT NULL
    )
""")
conn.commit()

# Insert data
for rawIndex, line in enumerate(lines, start=1):
    # Insert a placeholder row with versionNum 0
    cursor.execute(
        "INSERT INTO files (rawNum, versionNum, embedPercentage, cutoff) VALUES (?, ?, ?, ?)",
        (rawIndex, 0, 0, 0)
    )
    
    for versionIndex, pair in enumerate(line):
        cutoff, embedPercentage = pair
        cursor.execute(
            "INSERT INTO files (rawNum, versionNum, embedPercentage, cutoff) VALUES (?, ?, ?, ?)",
            (rawIndex, versionIndex + 2, embedPercentage, cutoff)
        )

conn.commit()
conn.close()
print("Database updated successfully.")
