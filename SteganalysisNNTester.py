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
import random

inputsList = []
outputsList = []

saveFolder = r"C:\Users\iniga\Datasets\Custom\NPY\AI Models"

modelCode = input("What is the model path?: ").strip().strip('"')
model = tf.keras.models.load_model(modelCode)
print("Old model loaded!")

# Testing AI - It will get 1k new images to check, and ill get an average of how wrong it is
def load_test_sample(filePath, dbPath):
    # Load the .npy file
    x = np.load(filePath).astype(np.float32)  # shape (256, 256)
    x = np.expand_dims(x, axis=0)  # batch dimension for model.predict()

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
    y_true = cursor.fetchone()[0]
    conn.close()

    return x, y_true

testFolder = r"C:\Users\iniga\Datasets\Custom\NPY\Testing"

testFiles = [os.path.join(testFolder, f) for f in os.listdir(testFolder) if f.endswith(".npy")]

errors = []

for filePath in testFiles:
    x_test, y_true = load_test_sample(filePath, "SteganalysisNNTrainingDatabase.db")
    y_pred = model.predict(x_test, verbose=2)[0][0]  # predicted value
    error = abs(y_pred - y_true)          # absolute error
    errors.append(error)

# Average error
average_error = sum(errors) / len(errors)
print(f"Average absolute error on test set: {average_error *100}%")