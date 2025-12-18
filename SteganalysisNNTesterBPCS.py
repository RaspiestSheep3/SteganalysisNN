#Imports
import tensorflow as tf 
from tensorflow import keras 
import tensorflow.keras.backend as K # type: ignore
from tensorflow.keras.optimizers import Adam # type: ignore
import datetime
import os
from plyer import notification
import numpy as np
import sqlite3

inputsList = []
outputsList = []

modelCode = input("What is the model path?: ").strip().strip('"')
model = tf.keras.models.load_model(modelCode)
print("Old model loaded!")

# Testing AI - It will get 1k new images to check, and ill get an average of how wrong it is
def load_test_sample(filePath, dbPath):
    # Load the .npy file
    x = np.load(filePath).astype(np.float32)  # shape (256, 256)
    x = np.expand_dims(x, axis=-1)  # add channel
    x = np.expand_dims(x, axis=0)   # add batch

    # Get true label from SQLite
    fileName = os.path.basename(filePath)
    fileStripped = os.path.splitext(fileName)[0]
    rawNum, versionNum = fileStripped.split("_")

    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT embedPercentage FROM files WHERE rawNum=? AND versionNum=?",
        (rawNum, versionNum)
    )
    y_true = cursor.fetchone()[0] / 100
    conn.close()

    return x, y_true

testFolder = r"C:\Users\iniga\Datasets\Custom\NPY\New Testing"

testFiles = [os.path.join(testFolder, f) for f in os.listdir(testFolder) if f.endswith(".npy")]

correct = 0
total = 0

BUCKET_EDGES = [0.0, 0.01, 0.03, 0.05, 0.10, 1.0]  # fractions, not %
NUM_BUCKETS = len(BUCKET_EDGES) - 1

def embedToBucket(embed):
    for i in range(len(BUCKET_EDGES) - 1):
        if BUCKET_EDGES[i] <= embed < BUCKET_EDGES[i + 1]:
            return i
    return len(BUCKET_EDGES) - 2

errors = []

for filePath in testFiles:
    x_test, y_true = load_test_sample(filePath, "SteganalysisNNTrainingDatabaseBPCS.db")
    bucketPred, regPred = model.predict(x_test, verbose = 0)

    trueBucket = embedToBucket(y_true)
    predBucket = np.argmax(bucketPred[0])

    if trueBucket == predBucket:
        correct += 1
    
    bucketIdx = np.argmax(bucketPred[0])
    low = BUCKET_EDGES[bucketIdx]
    high = BUCKET_EDGES[bucketIdx + 1]

    predictedEmbed = np.clip(regPred[0][0], low, high)
    error = abs(predictedEmbed - y_true)          # absolute error
    errors.append(error)
    
    total += 1
    
    if(total % 100) == 0:
        print(f"Processed {total}")
    

print("Bucket accuracy:", correct / total)
average_error = sum(errors) / len(errors)
print(f"Average absolute error on test set: {average_error *100}%")