# This is a sample Python script.
import sys
import threading
import time

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QFileDialog
import configparser
import StripchatRecorder
from StripchatRecorder import startRecording
from PySide6 import QtCore, QtWidgets
import Utils
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


class StripchatUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StripchatRecorder")
        self.selectedFiles = []
        self.setMinimumSize(800, 500)
        self.runProg = True
        # Create tabs
        self.recList = [[],[]]
        self.tabs = QtWidgets.QTabWidget()
        self.recThread = threading.Thread(target=StripchatRecorder.startRecording, args=(self.recList,))
        # Create Tab 1
        self.tab1 = QtWidgets.QWidget()
        self.tab1Layout = QtWidgets.QHBoxLayout(self.tab1)
        self.Config = configparser.ConfigParser()
        # Create Left Panel
        self.leftPanel = QtWidgets.QVBoxLayout()
        self.mainDir = sys.path[0]
        self.Config.read(self.mainDir + '/config.conf')
        self.wanted_model = open(self.Config.get('paths', 'wishlist'), 'r').read().splitlines()

        # Create the layout and add the first QLineEdit widget
        self.lineEditsLayout = QtWidgets.QVBoxLayout()
        self.lineEdits = [QtWidgets.QLineEdit() for _ in range(len(self.wanted_model)+1)]
        # print(len(self.wanted_model))

        self.lineEditsWidget = QtWidgets.QWidget()
        self.lineEditsVbox = QtWidgets.QVBoxLayout()
        self.lineEditsWidget.setLayout(self.lineEditsVbox)
        self.lineEditsScrollArea = QtWidgets.QScrollArea()
        self.lineEditsScrollArea.setWidget(self.lineEditsWidget)
        self.lineEditsScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.lineEditsScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.lineEditsScrollArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.lineEditsScrollArea.setWidgetResizable(True)
        self.lineEditsScrollArea.setStyleSheet("QWidget {border: 1px solid gray; border-radius: 5px;}")

        # Create the button to add new QLineEdit widgets
        self.addButton = QtWidgets.QPushButton("Add Model")
        self.addButton.clicked.connect(self.addLineEdit)
        # self.addButton.setAlignment(Qt.AlignmentFlag.AlignBottom)
        # Create a widget to hold the line edits layout
        # Create a scroll area to hold the line edits widget

        # Add the scroll area to the left panel
        self.leftPanel.addWidget(self.lineEditsScrollArea)

        for i in (range(len(self.lineEdits))):
            if i < len(self.wanted_model):
                # print(i)
                self.lineEdits[i].setText(self.wanted_model[i])
            self.lineEditsVbox.addWidget(self.lineEdits[i])


        # Add the button to the left panel
        # self.leftPanel.addWidget(self.addButton, alignment=QtCore.Qt.AlignBottom)
        # Create TextInput Box
        self.inputStream = QtWidgets.QLineEdit()
        self.inputStream.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Create Start Button
        self.startButton = QtWidgets.QPushButton("Start")
        self.startButton.clicked.connect(self.startRecording)

        # Create Stop Button
        self.stopButton = QtWidgets.QPushButton("Stop")
        self.stopButton.clicked.connect(self.stopRecording)

        self.applyModelsButton = QtWidgets.QPushButton("Apply Changes")
        self.applyModelsButton.clicked.connect(self.applyModel)
        # self.stopButton.clicked.connect(self.stopRecording)

        # Add TextInput Box and Start Button to Left Panel
        # self.leftPanel.addWidget(self.inputStream, 2)
        self.tab1ActionRows = QtWidgets.QHBoxLayout()
        self.tab1InputRows = QtWidgets.QHBoxLayout()
        self.tab1InputRows.addWidget(self.addButton, 1)
        self.tab1InputRows.addWidget(self.applyModelsButton, 1)
        self.tab1ActionRows.addWidget(self.startButton, 1)
        self.tab1ActionRows.addWidget(self.stopButton, 1)
        self.leftPanel.addLayout(self.tab1InputRows, 1)
        self.leftPanel.addLayout(self.tab1ActionRows, 1)
        # self.leftPanel.addWidget(self.startButton, 1)

        # Create Right Panel
        self.rightPanel = QtWidgets.QVBoxLayout()

        # Create Bordered Textbox
        self.streamerBox = QtWidgets.QGroupBox("Recording Streamer")
        self.streamerBox.setStyleSheet("QGroupBox {border: 1px solid gray; border-radius: 5px; padding-top: 10px}")

        # Create Label
        self.streamerLabel = QtWidgets.QLabel("No streamer selected")
        self.streamerLabel.setAlignment(QtCore.Qt.AlignTop)

        self.recordingBox = QtWidgets.QWidget()
        self.recordingBox.setStyleSheet("QWidget {border: 1px solid gray; border-radius: 5px; padding-top: 10px}")
        self.recordingBoxLayout = QtWidgets.QVBoxLayout()
        self.recordingBox.setLayout(self.recordingBoxLayout)

        # self.recordingHistory = QtWidgets.QLabel("Recording History")
        # self.recordingHistory.setAlignment(QtCore.Qt.AlignTop)

        # Add Label to Bordered Textbox
        self.streamerLayout = QtWidgets.QVBoxLayout(self.streamerBox)
        self.streamerLayout.addWidget(self.streamerLabel)

        self.streamerDisplayWidget = QtWidgets.QWidget()
        self.streamerDisplayVbox = QtWidgets.QVBoxLayout()
        self.streamerDisplayWidget.setLayout(self.streamerDisplayVbox)
        self.recordingScrollArea = QtWidgets.QScrollArea(self.recordingBox)
        self.recordingScrollArea.setWidget(self.streamerDisplayWidget)
        self.recordingScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.recordingScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.recordingScrollArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.recordingScrollArea.setWidgetResizable(True)
        self.recordingScrollArea.setStyleSheet("QWidget {border: 1px solid gray; border-radius: 5px;}")
        # Add Bordered Textbox to Right Panel
        self.rightPanel.addWidget(self.streamerBox, 1)
        self.rightPanel.addWidget(self.recordingScrollArea, 1)

        # Add Left and Right Panel to Tab 1
        self.tab1Layout.addLayout(self.leftPanel, 1)
        self.tab1Layout.addLayout(self.rightPanel, 1)

        self.fixVideoTabWidget = QtWidgets.QWidget()
        self.fixVideoTabLayout = QtWidgets.QHBoxLayout()
        self.fixVideoTabWidget.setLayout(self.fixVideoTabLayout)

        self.addFileBtn = QtWidgets.QPushButton("Select Files")
        # self.btn.clicked.connect(self.getfile)

        self.flineEditsWidget = QtWidgets.QWidget()
        self.flineEditsVbox = QtWidgets.QVBoxLayout()
        self.flineEditsVbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.flineEditsWidget.setLayout(self.flineEditsVbox)
        self.flineEditsScrollArea = QtWidgets.QScrollArea()
        self.flineEditsScrollArea.setWidget(self.flineEditsWidget)
        self.flineEditsScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.flineEditsScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.flineEditsScrollArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.flineEditsScrollArea.setWidgetResizable(True)
        self.flineEditsScrollArea.setStyleSheet("QWidget {border: 1px solid gray; border-radius: 5px;}")

        self.fAddButton = QtWidgets.QPushButton("Select Video")
        self.fAddButton.clicked.connect(self.getfiles)

        self.fClearButton = QtWidgets.QPushButton("Clear Selection")
        self.fClearButton.clicked.connect(self.clearSelection)

        self.fRunButton = QtWidgets.QPushButton("Start Fix")
        self.fRunButton.clicked.connect(self.startFix)

        self.fixVideoButtonWidget1 = QtWidgets.QWidget()
        self.fixVideoButtonLayout1 = QtWidgets.QHBoxLayout()
        self.fixVideoButtonWidget1.setLayout(self.fixVideoButtonLayout1)
        self.fixVideoButtonLayout1.addWidget(self.fAddButton)
        self.fixVideoButtonLayout1.addWidget(self.fClearButton)

        self.fixVideoButtonWidget2 = QtWidgets.QWidget()
        self.fixVideoButtonLayout2 = QtWidgets.QHBoxLayout()
        self.fixVideoButtonWidget2.setLayout(self.fixVideoButtonLayout2)
        self.fixVideoButtonLayout2.addWidget(self.fRunButton)

        self.PPLeftPanelWidget = QtWidgets.QWidget()
        self.PPLeftPanelLayout = QtWidgets.QVBoxLayout()
        self.PPLeftPanelLayout.addWidget(self.flineEditsScrollArea)
        self.PPLeftPanelLayout.addWidget(self.fixVideoButtonWidget1)
        self.PPLeftPanelLayout.addWidget(self.fixVideoButtonWidget2)
        # self.PPLeftPanelWidget.setStyleSheet("background-color: yellow")
        self.PPLeftPanelWidget.setLayout(self.PPLeftPanelLayout)

        self.PPRightPanelWidget = QtWidgets.QWidget()
        self.PPRightPanelLayout = QtWidgets.QVBoxLayout()
        # self.PPRightPanelWidget.setStyleSheet("background-color: red")
        self.PPRightPanelWidget.setLayout(self.PPRightPanelLayout)


        self.fixVideoTabLayout.addWidget(self.PPLeftPanelWidget, 1)
        self.fixVideoTabLayout.addWidget(self.PPRightPanelWidget, 1)


        self.tabSetting = QtWidgets.QWidget()
        self.tabSettingLayout = QtWidgets.QVBoxLayout()
        self.tabFormLayout = QtWidgets.QFormLayout()
        self.tabSetting.setLayout(self.tabSettingLayout)

        self.targetDirTextEdit = QtWidgets.QLineEdit()
        self.targetDirTextEdit.setText(self.Config.get('paths', 'save_directory'))
        self.wantedModelDirTextEdit = QtWidgets.QLineEdit()
        self.wantedModelDirTextEdit.setText(self.Config.get('paths', 'wishlist'))

        self.tabFormLayout.addRow("Save Recording Directory", self.targetDirTextEdit)
        self.tabFormLayout.addRow("Wanted Model File Directory", self.wantedModelDirTextEdit)

        self.applySetting = QtWidgets.QPushButton("Apply")
        self.applySetting.clicked.connect(self.applyConfig)
        self.settingActionRow = QtWidgets.QHBoxLayout();
        self.settingActionRow.addWidget(self.applySetting)
        self.tabSettingLayout.addLayout(self.tabFormLayout)
        self.tabSettingLayout.addLayout(self.settingActionRow)
        # Add Tab 1 to the tabs
        self.tabs.addTab(self.tab1, "Recording")
        self.tabs.addTab(self.fixVideoTabWidget, "Fix Videos")
        self.tabs.addTab(self.tabSetting, "Setting")


        # Add tabs to the main window
        self.setCentralWidget(self.tabs)

        # Set window properties
        self.setWindowTitle("StripchatUI")
        self.setGeometry(100, 100, 800, 600)

        # Update the text every second
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateUI)
        self.timer.start(1000)

    def addLineEdit(self):
        # Add a new QLineEdit widget to the list and layout
        newLineEdit = QtWidgets.QLineEdit()
        self.lineEdits.append(newLineEdit)
        self.lineEditsVbox.addWidget(newLineEdit)
        # for wid in self.lineEdits:
        #     wid.setStyleSheet("background-color: yellow")

    def addSelectedFile(self, filename):
        # Add a new QLineEdit widget to the list and layout
        newLineEdit = QtWidgets.QLineEdit()
        newLineEdit.setText(filename)
        self.selectedFiles.append(filename)
        self.fixSelectedFileListLayout.addWidget(newLineEdit)
        # for wid in self.lineEdits:
        #     wid.setStyleSheet("background-color: yellow")

    def applyModel(self):
        with open(self.Config.get('paths', 'wishlist'), 'w') as file:
            file.write('\n'.join(i.text() for i in self.lineEdits))

    def applyConfig(self):
        self.Config.set('paths', 'wishlist', self.wantedModelDirTextEdit.text())
        self.Config.set('paths', 'save_directory', self.targetDirTextEdit.text())
        with open(self.mainDir + '/config.conf', 'w') as configfile:
            self.Config.write(configfile)
    def updateUI(self):
        print(Utils.format_model_to_UI(self.recList[0]))
        self.streamerLabel.setText(Utils.format_model_to_UI(self.recList[0]))

        for i in reversed(range(self.streamerDisplayVbox.count())):
            self.streamerDisplayVbox.itemAt(i).widget().setParent(None)

        for history in self.recList[1]:
            label = QLabel(Utils.format_recording_history_to_UI(history))
            label.setAlignment(QtCore.Qt.AlignTop)
            if history["status"] == "Stopped Recording":
                label.setStyleSheet("background-color: rgba(168, 0, 0, 204);")
            self.streamerDisplayVbox.addWidget(label)
        # self.recordingHistory.setText(Utils.format_recording_history_to_UI(self.recList[1]))

    def startRecording(self):
        self.runProg = True
        self.recThread.start()

    def getfiles(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dlg.setMimeTypeFilters(
            {
                "video/mp4"
            }
        )
        filenames = []

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            for file in filenames:
                if file not in self.selectedFiles:
                    self.selectedFiles.append(file)

            for i in reversed(range(self.flineEditsVbox.count())):
                self.flineEditsVbox.itemAt(i).widget().setParent(None)
            for filename in self.selectedFiles:
                label = QLabel(filename)
                label.setAlignment(QtCore.Qt.AlignTop)
                delButton = QtWidgets.QPushButton("Remove")
                delButton.clicked.connect(self.addLineEdit)
                selectedFileItemWidget = QtWidgets.QWidget()
                selectedFileItemLayout = QtWidgets.QHBoxLayout()
                selectedFileItemLayout.addWidget(label)
                selectedFileItemLayout.addWidget(delButton)
                selectedFileItemWidget.setLayout(selectedFileItemLayout)
                # selectedFileItemWidget.setStyleSheet("background-color: yellow")

                newLineEdit = QtWidgets.QLineEdit()
                newLineEdit.setText(filename)
                newLineEdit.setEnabled(False)
                self.flineEditsVbox.addWidget(newLineEdit)

                #self.fixSelectedFileListLayout.addWidget(selectedFileItemWidget)
                print(filename)

                # newLineEdit = QtWidgets.QLineEdit()
                # self.lineEdits.append(newLineEdit)
                # self.lineEditsVbox.addWidget(newLineEdit)
    def startFix(self):
       print("Start Fixing")
       for file in self.selectedFiles:
           print("START REPAIR THREAD")

           def target():
               Utils.repair_mp4_file_ffmpeg(file)

           # output_file = Utils.repair_mp4_file_ffmpeg(file)
           thread = threading.Thread(target=target)
           thread.daemon = True
           thread.start()
    def clearSelection(self):
        print("Clear Selection")
        self.selectedFiles.clear()
    def stopRecording(self):
        print("STOP")
        StripchatRecorder.stopRecording()
        self.recThread = threading.Thread(target=StripchatRecorder.startRecording, args=(self.recList,))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # recList = [[]]
    # Start recording on a separate thread
    # recThread = threading.Thread(target=startRecording, args=(recList,))
    # recThread.start()
    # while True:
    #     print("reclist: ", recList[0])
    #     time.sleep(1)
    app = QtWidgets.QApplication([])
    app.setStyle('Fusion')
    ui = StripchatUI()
    ui.show()
    app.exec_()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
