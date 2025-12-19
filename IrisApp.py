import os
import sys
import json
import ctypes
import numpy as np
from PIL import Image
import tensorflow as tf 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from tensorflow import keras
from PyQt5.QtWidgets import *

# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.
def loadStyleSheet(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Iris.App")
app = QApplication(sys.argv)
app.setWindowIcon(QIcon("icon.png"))
app.setStyleSheet(loadStyleSheet("style.qss"))

#JSON Stuff
JSON_FILENAME = "Settings.json"

if(os.path.isfile(JSON_FILENAME)):
    with open(JSON_FILENAME, "r") as fileHandle:
        jsonData = json.load(fileHandle)
else:
    jsonData = {
        "Rod Path" : "None",
        "Cone Path" : "None",
        "Analyse BPCS" : "Y",
        "Analyse LSB" : "Y"
    }
    
    with open(JSON_FILENAME, "w", encoding="utf-8") as f:
        json.dump(jsonData, f, indent=4)

class PngDropArea(QLabel):
    fileDropped = pyqtSignal(str)

    def __init__(self):
        super().__init__("Drop PNG image here ⤒")
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        urls = event.mimeData().urls()
        if len(urls) == 1 and urls[0].toLocalFile().lower().endswith(".png"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        path = event.mimeData().urls()[0].toLocalFile()
        self.fileDropped.emit(path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Iris")

        # Central widget
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        # Main horizontal layout
        mainLayout = QHBoxLayout(centralWidget)

        # -------------------------
        # Left panel: File Display
        # -------------------------
        fileDisplayLayout = QVBoxLayout()
        self.dropArea = PngDropArea()
        self.dropArea.setObjectName("PNGDropArea")
        self.dropArea.fileDropped.connect(self.onImageLoaded)
        self.dropArea.setFixedSize(768, 768)

        
        fileDisplayLayout.addStretch()
        fileDisplayLayout.addWidget(self.dropArea, alignment=Qt.AlignCenter)
        fileDisplayLayout.addStretch()

        mainLayout.addLayout(fileDisplayLayout)
        
        self.loadedImagePath = None

        # -------------------------
        # Right panel: Controls
        # -------------------------
        rightPanel = QWidget()
        rightLayout = QVBoxLayout(rightPanel)

        # Analysis Options Group
        analysisGroup = QGroupBox("Analysis Options")
        analysisLayout = QVBoxLayout()
        self.BPCScheckbox = QCheckBox("Analyse for BPCS")
        self.LSBcheckbox = QCheckBox("Analyse for LSB")
        analysisLayout.addWidget(self.BPCScheckbox)
        analysisLayout.addWidget(self.LSBcheckbox)
        
        analysisGroup.setLayout(analysisLayout)

        # AI Model Paths Group
        pathGroup = QGroupBox("AI Model Paths")
        pathLayout = QVBoxLayout()
        self.rodPathInput = QLineEdit()
        self.rodPathInput.setPlaceholderText("LSB Detector Path")
        self.rodPathInput.setMinimumWidth(800)
        pathLayout.addWidget(self.rodPathInput, alignment=Qt.AlignCenter)
        
        self.conePathInput = QLineEdit()
        self.conePathInput.setPlaceholderText("BPCS Detector Path")
        self.conePathInput.setMinimumWidth(800)
        pathLayout.addWidget(self.conePathInput, alignment=Qt.AlignCenter)
        
        self.setPathsButton = QPushButton("Set AI Model Paths")
        self.setPathsButton.setCursor(Qt.PointingHandCursor)
        self.setPathsButton.clicked.connect(self.SetAIModelPaths)
        self.setPathsButton.setMinimumWidth(500)
        pathLayout.addWidget(self.setPathsButton, alignment=Qt.AlignCenter)
        
        pathGroup.setLayout(pathLayout)

        #Image Settings Group
        imageSettingsGroup = QGroupBox("Image and Scan Settings")
        imageSettingsLayout = QVBoxLayout()

        imageSettingsButton = QPushButton("Clear Loaded Image")
        imageSettingsButton.setCursor(Qt.PointingHandCursor)
        imageSettingsButton.clicked.connect(self.ClearLoadedImage)
        imageSettingsButton.setMinimumWidth(500)
        imageSettingsLayout.addWidget(imageSettingsButton, alignment=Qt.AlignCenter)
        
        runScanButton = QPushButton("Run Image Scan")
        runScanButton.setCursor(Qt.PointingHandCursor)
        runScanButton.clicked.connect(self.RunImageScan)
        runScanButton.setMinimumWidth(500)
        imageSettingsLayout.addWidget(runScanButton, alignment=Qt.AlignCenter)
        
        imageSettingsGroup.setLayout(imageSettingsLayout)
        
        #Scan Results Group
        scanResultsGroup = QGroupBox("Scan Results")
        scanResultsLayout = QHBoxLayout()
        
        #Defining 2 sublayouts - 1 for LSB, one for BPCS
        LSBScanResultsLayout = QVBoxLayout()
        BPCSScanResultsLayout = QVBoxLayout()
        
        #Populatoinging LSB scan resulst
        self.LSBPlane1Result = QLabel("LSB Plane 1 : 12.34%")
        self.LSBPlane2Result = QLabel("LSB Plane 2 : 12.34%")
        self.LSBPlane3Result = QLabel("LSB Plane 3 : 12.34%")
        
        for layout in [self.LSBPlane1Result, self.LSBPlane2Result, self.LSBPlane3Result]:
            LSBScanResultsLayout.addWidget(layout, alignment=Qt.AlignCenter)
        
        #Same stuff for BPCS
        self.BPCSPlane1Result = QLabel("BPCS Plane 1 : 12.34%")
        self.BPCSPlane2Result = QLabel("BPCS Plane 2 : 12.34%")
        self.BPCSPlane3Result = QLabel("BPCS Plane 3 : 12.34%")
        
        for layout in [self.BPCSPlane1Result, self.BPCSPlane2Result, self.BPCSPlane3Result]:
            BPCSScanResultsLayout.addWidget(layout, alignment=Qt.AlignCenter)
        
        scanResultsLayout.addLayout(LSBScanResultsLayout)
        scanResultsLayout.addLayout(BPCSScanResultsLayout)
        
        scanResultsGroup.setLayout(scanResultsLayout)
        # Add groups to right panel
        rightLayout.addWidget(analysisGroup)
        rightLayout.addWidget(pathGroup)
        rightLayout.addWidget(imageSettingsGroup)
        rightLayout.addWidget(scanResultsGroup)
        #rightLayout.addStretch()  # Push everything to the top

        # Add right panel to main layout
        mainLayout.addWidget(rightPanel)
        
        #AI model stuff
        self.rodModel = None
        self.coneModel = None
        
        #Setting the JSON data
        self.LSBcheckbox.setChecked(jsonData["Analyse LSB"] == "Y")
        self.BPCScheckbox.setChecked(jsonData["Analyse BPCS"] == "Y")
        self.rodPathInput.setText(jsonData["Rod Path"] if jsonData["Rod Path"] != "None" else "")
        self.conePathInput.setText(jsonData["Cone Path"] if jsonData["Cone Path"] != "None" else "")

        if(jsonData["Rod Path"] != "None" and os.path.isfile(jsonData["Rod Path"])):
            self.rodModel = tf.keras.models.load_model(jsonData["Rod Path"])
        if(jsonData["Cone Path"] != "None" and os.path.isfile(jsonData["Cone Path"])):
            self.coneModel = tf.keras.models.load_model(jsonData["Cone Path"])        
        
    def SetAIModelPaths(self):
        #Doign this stirp bcs when you use the copy path function in windows it puts the "" for some reason
        rodPath = self.rodPathInput.text().strip().strip('"')
        conePath = self.conePathInput.text().strip().strip('"')

        #Invalid pathing
        if("" in [rodPath, conePath]):
            return
        
        #Checking the files actually exist
        if(not os.path.isfile(rodPath)) or (not os.path.isfile(conePath)):
            return
        
        #Checking both paths end in .keras
        if(os.path.splitext(rodPath)[1] != ".keras") or (os.path.splitext(conePath)[1] != ".keras"):
            return
        
        #Loading in both models
        self.rodModel = tf.keras.models.load_model(rodPath)
        self.coneModel = tf.keras.models.load_model(conePath)
        
        #Saving the paths
        jsonData["Rod Path"] = rodPath
        jsonData["Cone Path"] = conePath
        
        with open(JSON_FILENAME, "w") as f:
           json.dump(jsonData, f, indent=4)

    def ClearLoadedImage(self):
        self.dropArea.clear()
        self.dropArea.setText("Drop PNG image here ⤒")
        self.loadedImagePath = None
    
    def RunImageScan(self):
        
        #Updating the JSON
        jsonData["Analyse BPCS"] = "Y" if self.BPCScheckbox.isChecked() else "N"
        jsonData["Analyse LSB"] = "Y" if self.LSBcheckbox.isChecked() else "N"
        
        with open(JSON_FILENAME, "w") as f:
           json.dump(jsonData, f, indent=4)
        
        #Creating the .npy of the image
        if(self.loadedImagePath == None):
            return
        
        img = Image.open(self.loadedImagePath)
        npys = []
        
        if(img.mode == "L"):
            #Grayscale
            arr = np.array(img, dtype=np.uint8)
            npys.append(arr)
        else:
            #Colour
            img = img.convert("RGB") if(img.mode != ("RGB", "RGBA")) else img
            r,g,b, = img.split()[:3]
            for channel in [r,g,b]:
                npys.append(np.array(channel, dtype=np.uint8))
        
        #LSB analysis
        LSBResults = []
        if(self.LSBcheckbox.isChecked()):
            for arr in npys:
                arr = arr & 1
                arr = np.expand_dims(arr, axis=0)
                predicition = self.rodModel.predict(arr, verbose=0)[0][0] * 100
                
                predicition = max(predicition, 0)
                predicition = min(predicition, 100)
                predicition = "{:.2f}".format(predicition)
                
                LSBResults.append(predicition)
        
        #BPCS analysis
        BPCSResults = []
        if(self.BPCScheckbox.isChecked()):
            BUCKET_EDGES = [0.0, 0.01, 0.03, 0.05, 0.10, 1.0] 
            
            for arr in npys:
                arr = arr.astype(np.float32) / 255
                
                arr = np.expand_dims(arr, axis=-1) 
                arr = np.expand_dims(arr, axis=0)
    
                bucketPred, regPred = self.coneModel.predict(arr, verbose = 0)
                
                bucketIdx = np.argmax(bucketPred[0])
                low = BUCKET_EDGES[bucketIdx]
                high = BUCKET_EDGES[bucketIdx + 1]

                predicition = np.clip(regPred[0][0], low, high) * 100
                predicition = max(predicition, 0)
                predicition = min(predicition, 100)
                predicition = "{:.2f}".format(predicition)
                
                BPCSResults.append(predicition)
        
        #Showing the results
        self.LSBPlane1Result.setText("LSB Plane 1 : " + f"{LSBResults[0]}%" if(len(LSBResults) >= 1) else "N/A")
        self.LSBPlane2Result.setText("LSB Plane 2 : " + f"{LSBResults[1]}%" if(len(LSBResults) >= 2) else "N/A")
        self.LSBPlane3Result.setText("LSB Plane 3 : " + f"{LSBResults[2]}%" if(len(LSBResults) >= 3) else "N/A")
        
        self.BPCSPlane1Result.setText("BPCS Plane 1 : " + f"{BPCSResults[0]}%" if(len(BPCSResults) >= 1) else "N/A")
        self.BPCSPlane2Result.setText("BPCS Plane 2 : " + f"{BPCSResults[1]}%" if(len(BPCSResults) >= 2) else "N/A")
        self.BPCSPlane3Result.setText("BPCS Plane 3 : " + f"{BPCSResults[2]}%" if(len(BPCSResults) >= 3) else "N/A")
        
    def onImageLoaded(self, path):
        pixmap = QPixmap(path).scaled(
            768, 768,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.dropArea.setPixmap(pixmap)
        self.loadedImagePath = path

# Create a Qt widget, which will be our window.
window = MainWindow()
window.show()  

# Start the event loop.
app.exec()