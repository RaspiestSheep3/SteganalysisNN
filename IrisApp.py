from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys

# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.
def loadStyleSheet(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

app = QApplication(sys.argv)
app.setStyleSheet(loadStyleSheet("style.qss"))

class PngDropArea(QLabel):
    fileDropped = pyqtSignal(str)

    def __init__(self):
        super().__init__("Drop PNG image here")
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

        # -------------------------
        # Right panel: Controls
        # -------------------------
        rightPanel = QWidget()
        rightLayout = QVBoxLayout(rightPanel)

        # Analysis Options Group
        analysisGroup = QGroupBox("Analysis Options")
        analysisLayout = QVBoxLayout()
        BPCScheckbox = QCheckBox("Analyse for BPCS")
        LSBcheckbox = QCheckBox("Analyse for LSB")
        analysisLayout.addWidget(BPCScheckbox)
        analysisLayout.addWidget(LSBcheckbox)
        
        analysisGroup.setLayout(analysisLayout)

        # AI Model Paths Group
        pathGroup = QGroupBox("AI Model Paths")
        pathLayout = QVBoxLayout()
        rodPathInput = QLineEdit()
        rodPathInput.setPlaceholderText("LSB Detector Path")
        rodPathInput.setMinimumWidth(800)
        pathLayout.addWidget(rodPathInput, alignment=Qt.AlignCenter)
        
        conePathInput = QLineEdit()
        conePathInput.setPlaceholderText("BPCS Detector Path")
        conePathInput.setMinimumWidth(800)
        pathLayout.addWidget(conePathInput, alignment=Qt.AlignCenter)
        
        setPathsButton = QPushButton("Set AI Model Paths")
        setPathsButton.setMinimumWidth(500)
        pathLayout.addWidget(setPathsButton, alignment=Qt.AlignCenter)
        
        pathGroup.setLayout(pathLayout)

        #Image Settings Group
        imageSettingsGroup = QGroupBox("Image and Scan Settings")
        imageSettingsLayout = QVBoxLayout()

        imageSettingsButton = QPushButton("Clear Loaded Image")
        imageSettingsButton.setMinimumWidth(500)
        imageSettingsLayout.addWidget(imageSettingsButton, alignment=Qt.AlignCenter)
        
        runScanButton = QPushButton("Run Image Scan")
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
        LSBPlane1Result = QLabel("LSB Plane 1 : 12.34%")
        LSBPlane2Result = QLabel("LSB Plane 2 : 12.34%")
        LSBPlane3Result = QLabel("LSB Plane 3 : 12.34%")
        
        for layout in [LSBPlane1Result, LSBPlane2Result, LSBPlane3Result]:
            LSBScanResultsLayout.addWidget(layout, alignment=Qt.AlignCenter)
        
        #Same stuff for BPCS
        BPCSPlane1Result = QLabel("BPCS Plane 1 : 12.34%")
        BPCSPlane2Result = QLabel("BPCS Plane 2 : 12.34%")
        BPCSPlane3Result = QLabel("BPCS Plane 3 : 12.34%")
        
        for layout in [BPCSPlane1Result, BPCSPlane2Result, BPCSPlane3Result]:
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

    def the_button_was_clicked(self):
        print("Clicked!")

    def the_button_was_toggled(self, checked):
        print("Checked?", checked)
        
    def onImageLoaded(self, path):
        pixmap = QPixmap(path).scaled(
            768, 768,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.dropArea.setPixmap(pixmap)

# Create a Qt widget, which will be our window.
window = MainWindow()
window.show()  # IMPORTANT!!!!! Windows are hidden by default.

# Start the event loop.
app.exec()


# Your application won't reach here until you exit and the event
# loop has stopped.
