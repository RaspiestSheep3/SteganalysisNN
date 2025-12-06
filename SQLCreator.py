import sqlite3

database = r"Steganography\Steganalysis NN\SteganalysisNNTrainingDatabase.db"

lines = []
with open(r"Steganography\Steganalysis NN\DataOverview.csv", "r") as fileHandle:
    linesRaw = fileHandle.readlines()
    lines = [line.strip("\n").split(",") for line in linesRaw]

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
        print(f"rawIndex : {rawIndex}, version : {versionIndex}, % : {embedPercentage}")
        cursor.execute(
            "INSERT INTO files (rawNum, versionNum, embedPercentage) VALUES (?, ?, ?)",
            (rawIndex, versionIndex + 1, embedPercentage)
        )

conn.commit()
conn.close()
