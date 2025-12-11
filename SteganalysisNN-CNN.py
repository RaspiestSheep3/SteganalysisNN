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

saveFolder = r"C:\Users\iniga\Datasets\Custom\NPY\AI Models\CNN"

def SaveModel(extraCode = ""):
    if(extraCode) != "":
        extraCode = "-" + extraCode
    
    filename = f"model{datetime.datetime.now().strftime('%d.%m.%y-%H.%M.%S')}{extraCode}.keras"
    full_path = os.path.join(saveFolder, filename)
    model.save(full_path)
    notification.notify(
        title="Model Saved",
        message=f"Successfully saved model{filename}",
        timeout=5
    )

def DataGenerator(filePaths, dbPath, batchSize=16, shuffle=True):
    numFiles = len(filePaths)
    
    while True:  # Keras requires an infinite loop for generators
        if shuffle:
            random.shuffle(filePaths)
        
        
        for offset in range(0, numFiles, batchSize):
            batchFiles = filePaths[offset:offset+batchSize]
            batchInputs = []
            batchOutputs = []
            
            conn = sqlite3.connect(dbPath)
            cursor = conn.cursor()

            for file in batchFiles:
                x = np.load(file)
                batchInputs.append(x)

                #Processing the file 
                #print(f"Index : {filePaths.index(file)}, File : {file}")
                fileStripped = file.strip(r"C:\Users\iniga\Datasets\Custom\NPY\Full/").strip(".npy")
                [rawNum, versionNum] = fileStripped.split("_")
                
                # Assuming table 'labels' with columns 'filename' and 'label'
                cursor.execute("SELECT embedPercentage FROM files WHERE rawNum=? AND versionNum=?", (rawNum, versionNum))
                y = cursor.fetchone()[0]
                batchOutputs.append(y)

            conn.close()  # close after batch
            batchInputs = np.array(batchInputs)
            batchOutputs = np.array(batchOutputs)
            yield batchInputs, batchOutputs
        

model = keras.Sequential([
    keras.layers.Input(shape=(256, 256, 1)),
    keras.layers.Conv2D(32, (3,3), activation='relu'),
    keras.layers.MaxPooling2D(),
    keras.layers.Conv2D(64, (3,3), activation='relu'),
    keras.layers.MaxPooling2D(),
    keras.layers.Conv2D(128, (3,3), activation='relu'),
    keras.layers.Flatten(),
    keras.layers.Dense(256, activation='relu'),
    keras.layers.Dense(1, activation='linear')
])

# Loading in old model, setting values
numEpochs = int(input("Epoch number: "))
shouldLoadOldModel = input("Should load in old model? (Y/N): ").strip().upper()

if shouldLoadOldModel == "Y":
    modelCode = input("What is the model code?: ").strip().strip('"')
    model = tf.keras.models.load_model(modelCode)
    print("Old model loaded!")

shouldSaveModel = input("Should save current model? (Y/N): ").strip().upper()

lossFunctionInput = input("USE MSE Loss Function (Y/N) : ").strip().upper()
if(lossFunctionInput == "Y"):
    lossFunction = "mean_squared_error"
else:
    lossFunction = "mean_absolute_error"

# Let's tell our machine how to learn. This step is like giving it the rules of the game.
learningRate = float(input("Learning rate (default = 0.0001) : "))
model.compile(
    optimizer=Adam(learning_rate = tf.keras.optimizers.schedules.ExponentialDecay(
    initial_learning_rate=learningRate, decay_steps=500, decay_rate=1, staircase=True)),  # The "coach" that helps the machine learn and improve.
    loss=lossFunction  # This tells it how bad its guesses are so it can try again.
)

#Creating TrainFilePaths
trainFilePaths = []
for i in range(1, 8901):
    for j in range(10):
        trainFilePaths.append(fr"C:\Users\iniga\Datasets\Custom\NPY\Full\{i}_{j}.npy")

# Time for the machine to learn! We show it our input-output pairs (data) many times (epochs).
batchSize = 16
trainGen = DataGenerator(trainFilePaths, 'SteganalysisNNTrainingDatabase.db', batchSize=batchSize)
stepsPerEpoch = len(trainFilePaths) // batchSize

if(numEpochs > 0):
    model.fit(trainGen, epochs=numEpochs, steps_per_epoch=stepsPerEpoch, verbose=1, batch_size=16)

# Saving AI
if(shouldSaveModel == "Y"):
    SaveModel()

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
    y_pred = model.predict(x_test)[0][0]  # predicted value
    error = abs(y_pred - y_true)          # absolute error
    errors.append(error)

# Average error
average_error = sum(errors) / len(errors)
print(f"Average absolute error on test set: {average_error *100}%")