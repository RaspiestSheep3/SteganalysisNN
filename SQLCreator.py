import sqlite3

database = r"SteganalysisNNTrainingDatabaseNew.db"

lines = []
with open(r"DataOverviewNew.csv", "r") as fileHandle:
    linesRaw = fileHandle.readlines()
    lines = [line.strip("\n").split(",") for line in linesRaw]

print(len(lines))

conn = sqlite3.connect(database)
cursor = conn.cursor()

cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS files (
        rawNum INTEGER NOT NULL,
        versionNum INTEGER NOT NULL,
        embedPercentage FLOAT NOT NULL
    )
""")
conn.commit()

for rawIndex, line in enumerate(lines, start=1):
    cursor.execute(
        "INSERT INTO files (rawNum, versionNum, embedPercentage) VALUES (?, ?, ?)",
        (rawIndex, 0, 0)
    )
    
    for versionIndex, item in enumerate(line):
        embedPercentage = (int(item) * 8) / 65536
        #print(f"rawIndex : {rawIndex}, version : {versionIndex}, % : {embedPercentage}")
        cursor.execute(
            "INSERT INTO files (rawNum, versionNum, embedPercentage) VALUES (?, ?, ?)",
            (rawIndex, versionIndex + 1, embedPercentage)
        )

conn.commit()
conn.close()
