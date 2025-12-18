import sqlite3

database = r"SteganalysisNNTrainingDatabaseBPCS.db"

lines = []
with open(r"DataOverviewBPCS.csv", "r") as fileHandle:
    linesRaw = fileHandle.readlines()
    lines = [line.strip("\n").split(",") for line in linesRaw]

print(len(lines))

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

for rawIndex, line in enumerate(lines, start=1):
    cursor.execute(
        "INSERT INTO files (rawNum, versionNum, embedPercentage, cutoff) VALUES (?, ?, ?, ?)",
        (rawIndex, 0, 0, 0)
    )
    
    for versionIndex, itemSet in enumerate(line):
        print(itemSet)
        itemSet = itemSet.strip("[").strip("]").split(",")
        cutoff = float(itemSet[0])
        embedPercentage = float(itemSet[1])
        #print(f"rawIndex : {rawIndex}, version : {versionIndex}, % : {embedPercentage}")
        cursor.execute(
            "INSERT INTO files (rawNum, versionNum, embedPercentage, cutoff) VALUES (?, ?, ?, ?)",
            (rawIndex, versionIndex + 2, embedPercentage, cutoff)
        )

conn.commit()
conn.close()
