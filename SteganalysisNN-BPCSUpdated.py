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

saveFolder = r"C:\Users\iniga\Datasets\AI Models\BPCS"

BUCKET_EDGES = [0.0, 0.01, 0.03, 0.05, 0.10, 1.0]  # fractions, not %
NUM_BUCKETS = len(BUCKET_EDGES) - 1

def embedToBucket(embed):
    for i in range(len(BUCKET_EDGES) - 1):
        if BUCKET_EDGES[i] <= embed < BUCKET_EDGES[i + 1]:
            return i
    return len(BUCKET_EDGES) - 2

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

    while True:  # Keras requires infinite generators
        if shuffle:
            random.shuffle(filePaths)

        for offset in range(0, numFiles, batchSize):
            batchFiles = filePaths[offset:offset + batchSize]

            batchInputs = []
            batchBuckets = []
            batchRegs = []

            conn = sqlite3.connect(dbPath)
            cursor = conn.cursor()

            for file in batchFiles:
                # Load input
                x = np.load(file).astype(np.float32)
                x = np.expand_dims(x, axis=-1)
                batchInputs.append(x)

                # Extract identifiers
                fileStripped = os.path.splitext(os.path.basename(file))[0]
                rawNum, versionNum = fileStripped.split("_")
                
                #print(f"File : {file}, Raw Num : {rawNum}, Version Num : {versionNum}")
                
                # Fetch embed percentage
                cursor.execute(
                    "SELECT embedPercentage FROM files WHERE rawNum=? AND versionNum=?",
                    (rawNum, versionNum)
                )
                embed = cursor.fetchone()[0]

                # Dual-head labels
                bucket = embedToBucket(embed)

                batchBuckets.append(bucket)
                batchRegs.append(embed)

            conn.close()

            # Convert to arrays
            batchInputs = np.array(batchInputs, dtype=np.float32)
            batchBuckets = keras.utils.to_categorical(batchBuckets, NUM_BUCKETS)
            batchRegs = np.array(batchRegs, dtype=np.float32)

            yield batchInputs, {
                "bucket": batchBuckets,
                "regression": batchRegs
            }
        

inputs = keras.Input(shape=(256,256,1))

x = keras.layers.Conv2D(32, 3, padding="same")(inputs)
x = keras.layers.BatchNormalization()(x)
x = keras.layers.ReLU()(x)
x = keras.layers.MaxPooling2D()(x)

x = keras.layers.Conv2D(64, 3, padding="same")(x)
x = keras.layers.BatchNormalization()(x)
x = keras.layers.ReLU()(x)
x = keras.layers.MaxPooling2D()(x)

x = keras.layers.Conv2D(128, 3, padding="same")(x)
x = keras.layers.BatchNormalization()(x)
x = keras.layers.ReLU()(x)
x = keras.layers.MaxPooling2D()(x)

x = keras.layers.Conv2D(256, 3, padding="same")(x)
x = keras.layers.BatchNormalization()(x)
x = keras.layers.ReLU()(x)

x = keras.layers.GlobalAveragePooling2D()(x)
x = keras.layers.Dense(128, activation="relu")(x)

# ---- HEAD 1: bucket classification ----
bucketOut = keras.layers.Dense(
    NUM_BUCKETS,
    activation="softmax",
    name="bucket"
)(x)

# ---- HEAD 2: regression ----
regOut = keras.layers.Dense(
    1,
    activation="linear",
    name="regression"
)(x)

model = keras.Model(inputs=inputs, outputs=[bucketOut, regOut])

# Loading in old model, setting values
numEpochs = int(input("Epoch number: "))
shouldLoadOldModel = input("Should load in old model? (Y/N): ").strip().upper()

if shouldLoadOldModel == "Y":
    modelCode = input("What is the model code?: ").strip().strip('"')
    model = tf.keras.models.load_model(modelCode)
    print("Old model loaded!")

shouldSaveModel = input("Should save current model? (Y/N): ").strip().upper()

# Let's tell our machine how to learn. This step is like giving it the rules of the game.
learningRate = float(input("Learning rate (default = 0.0001) : "))

#Creating TrainFilePaths
trainFilePaths = []
for i in range(1, 18901):
    for j in range(0,11):
        if j == 1:
            continue
        trainFilePaths.append(fr"C:\Users\iniga\Datasets\Custom\NPY\BPCS Full\{i}_{j}.npy")

batchSize = 16
trainGen = DataGenerator(trainFilePaths, 'SteganalysisNNTrainingDatabaseBPCS.db', batchSize=batchSize)
stepsPerEpoch = len(trainFilePaths) // batchSize

model.compile(
    optimizer=Adam(
        learning_rate=tf.keras.optimizers.schedules.CosineDecay(
            initial_learning_rate=learningRate,
            decay_steps=stepsPerEpoch * numEpochs
        )
    ),
    loss={
        "bucket": "categorical_crossentropy",
        "regression": tf.keras.losses.Huber(delta=0.01)
    },
    loss_weights={
        "bucket": 1.0,
        "regression": 0.5
    }
)

# Time for the machine to learn! We show it our input-output pairs (data) many times (epochs).
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

testFolder = r"C:\Users\iniga\Datasets\Custom\NPY\BPCS Testing"

testFiles = [os.path.join(testFolder, f) for f in os.listdir(testFolder) if f.endswith(".npy")]

errors = []

for filePath in testFiles:
    x_test, y_true = load_test_sample(filePath, "SteganalysisNNTrainingDatabaseBPCS.db")
    bucketPred, regPred = model.predict(x_test)

    bucketIdx = np.argmax(bucketPred[0])
    low = BUCKET_EDGES[bucketIdx]
    high = BUCKET_EDGES[bucketIdx + 1]

    predictedEmbed = np.clip(regPred[0][0], low, high)
    error = abs(predictedEmbed - y_true)          # absolute error
    errors.append(error)

# Average error
average_error = sum(errors) / len(errors)
print(f"Average absolute error on test set: {average_error *100}%")