import sys      # noqa
import json
from arducopter import Arducopter
from dji import Dji
from PyQt5.QtWidgets import (QWidget, QApplication, QMainWindow, QHBoxLayout,
                             QGridLayout, QDesktopWidget, qApp, QPushButton, QLabel,
                             QAction, QFileDialog, QGroupBox, QCheckBox, QMessageBox,
                             QComboBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
"""
A GUI front end generating NASA specific csv files from ArduCopter and DJI UAS
log files.
"""

ABOUT_TEXT = """
             """

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 350

ardu = Arducopter()
dji = Dji()


class ConvGUI(QMainWindow):
    """Class for GUI set up and all methods."""

    def __init__(self):
        """Initialize GUI."""
        super().__init__()
        self.initUI()

    def initUI(self):   # noqa
        """Set up GUI design."""
        # Initialize to zero for checking if waypoint
        # file was opened in arduGen function
        self.wpt_file = 0
        self.gcs_loc_chosen = 0
        self.gcs_loc_file = open("gcs-locations.json", "r")

        # __Actions__
        saveAct = QAction('&Save Location', self)
        saveAct.setShortcut('Ctrl+S')
        saveAct.setStatusTip('Choose save location.')
        saveAct.triggered.connect(self.saveLocation)

        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit Application')
        exitAct.triggered.connect(qApp.quit)

        # __Buttons__
        self.missionInsightBtn = QPushButton("Open Mission Insight File")
        self.missionInsightBtn.clicked.connect(self.openMI)

        self.arduCsvBtn = QPushButton("Open TLog...")
        self.arduCsvBtn.clicked.connect(self.openTlog)
        self.arduWptBtn = QPushButton("Open Waypoint...")
        self.arduWptBtn.clicked.connect(self.openWpt)
        self.arduGenBtn = QPushButton("Generate Files")
        self.arduGenBtn.clicked.connect(self.arduGen)
        self.arduGenBtn.setEnabled(False)

        self.djiLitBtn = QPushButton("Open Litchi log...")
        self.djiLitBtn.clicked.connect(self.openLitchi)
        self.djiBinBtn = QPushButton("Open DJI binary log...")
        self.djiBinBtn.clicked.connect(self.openBinary)
        self.djiGenBtn = QPushButton("Generate Files")
        self.djiGenBtn.clicked.connect(self.djiGen)
        self.djiGenBtn.setEnabled(False)

        # __Checkboxes__
        self.missionInsightChk = QCheckBox("File from Mission Insight program")
        self.missionInsightChk.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.missionInsightChk.setFocusPolicy(Qt.NoFocus)

        self.arduCsvChk = QCheckBox("TLog file from flight in .csv format")
        self.arduCsvChk.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.arduCsvChk.setFocusPolicy(Qt.NoFocus)
        self.arduWptChk = QCheckBox("Waypoint file for flight plan")
        self.arduWptChk.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.arduWptChk.setFocusPolicy(Qt.NoFocus)

        self.djiLitChk = QCheckBox("DJI Litchi csv file")
        self.djiLitChk.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.djiLitChk.setFocusPolicy(Qt.NoFocus)
        self.djiBinChk = QCheckBox("Binary DJI file")
        self.djiBinChk.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.djiBinChk.setFocusPolicy(Qt.NoFocus)

        # __Drop Down Menu__
        self.gcsLocationsMenu = QComboBox(self)
        self.gcsLocationsMenu.addItem("Select GCS Location")
        self.gcsLocations = json.load(self.gcs_loc_file)
        for location in self.gcsLocations:
            self.gcsLocationsMenu.addItem(location)

        for i in range(0, self.gcsLocationsMenu.count()):
            self.gcsLocationsMenu.setItemData(i, Qt.AlignCenter, Qt.TextAlignmentRole)

        self.gcsLocationsMenu.setEditable(True)
        self.gcsLocationsMenu.lineEdit().setReadOnly(True)
        self.gcsLocationsMenu.lineEdit().setAlignment(Qt.AlignCenter)

        self.gcsLocationsMenu.activated[str].connect(self.gcsLocationChosen)

        # __Labels__
        arduCsvLbl = QLabel("TLog file in csv format.")                 # noqa
        arduWptLbl = QLabel("Waypoint file for flight plan.")           # noqa

        # __Menubar__
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(saveAct)
        fileMenu.addAction(exitAct)

        # __StatusBar__
        self.statusBar().showMessage('Ready')

        # __Layout__
        grid1 = QGridLayout()
        grid1.addWidget(self.gcsLocationsMenu, 0, 1, 1, 2)
        grid1.addWidget(self.missionInsightBtn, 1, 0, 1, -1)
        grid1.addWidget(self.missionInsightChk, 2, 2)
        grid1.addWidget(self.arduCsvChk, 3, 0)
        grid1.addWidget(self.arduCsvBtn, 3, 1)
        grid1.addWidget(self.arduWptChk, 4, 0)
        grid1.addWidget(self.arduWptBtn, 4, 1)
        grid1.addWidget(self.arduGenBtn, 5, 0, 1, 2)
        grid1.addWidget(self.djiLitChk, 3, 3)
        grid1.addWidget(self.djiLitBtn, 3, 4)
        grid1.addWidget(self.djiBinChk, 4, 3)
        grid1.addWidget(self.djiBinBtn, 4, 4)
        grid1.addWidget(self.djiGenBtn, 5, 3, 1, -1)

        vert1 = QGroupBox()
        vert1.setLayout(grid1)

        hbox = QHBoxLayout()
        hbox.addWidget(vert1)

        centralWidget = QWidget()
        centralWidget.setLayout(hbox)
        self.setCentralWidget(centralWidget)

        self.setFixedSize(self.sizeHint())
        self.center()

        self.setWindowTitle('NASA File Generator')
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def gcsLocationChosen(self, location):
        if location != 'Select GCS Location':
            self.selected_gcs_loc = self.gcsLocations[location]
            self.gcs_loc_chosen = 1
        else:
            self.gcs_loc_chosen = 0

        self.buttonToggle()

    def openTlog(self):
        self.tlog_file = QFileDialog.getOpenFileName(
            self, 'Open file', None)[0]

        if self.tlog_file[-4:].lower() == ".csv":
            self.arduCsvChk.setChecked(True)
        else:
            msgBox = QMessageBox.warning(self, "Log Error", "Please choose a valid log file!")

        self.buttonToggle()

    def openWpt(self):
        self.wpt_file = QFileDialog.getOpenFileName(
            self, 'Open file', None)[0]

        if self.wpt_file[-10:].lower() == ".waypoints":
            self.arduWptChk.setChecked(True)
        else:
            msgBox = QMessageBox.warning(self, "Log Error", "Please choose a valid log file!")

        self.buttonToggle()

    def openMI(self):
        self.mi_file = QFileDialog.getOpenFileName(
            self, 'Open file', None)[0]

        if self.mi_file[-4:].lower() == ".csv":
            self.missionInsightChk.setChecked(True)
        else:
            msgBox = QMessageBox.warning(self, "Log Error", "Please choose a valid log file!")

        self.buttonToggle()

    def openLitchi(self):
        pass

    def openBinary(self):
        self.bin_file = QFileDialog.getOpenFileName(
            self, 'Open file', None)[0]

        if self.bin_file[-4:].lower() == ".csv":
            self.djiBinChk.setChecked(True)
        else:
            msgBox = QMessageBox.warning(self, "Log Error", "Please choose a valid log file!")

        self.buttonToggle()

    def buttonToggle(self):
        """Checks for conditions required to enable log generation buttons."""
        if (self.arduCsvChk.isChecked() and self.missionInsightChk.isChecked() and self.gcs_loc_chosen):
            self.arduGenBtn.setEnabled(True)
        else:
            self.arduGenBtn.setEnabled(False)
        if (self.djiBinChk.isChecked() and self.missionInsightChk.isChecked and self.gcs_loc_chosen):
            self.djiGenBtn.setEnabled(True)
        else:
            self.djiGenBtn.setEnabled(False)

    # QFileDialog:getSaveFileName will pass name even if it doesn't exist
    # unlike QFileDialog:getOpenFileName; Linux doesn't seem to care but
    # Windows definitely does
    def saveLocation(self):
        """Open save location dialog menu."""
        self.save_location = QFileDialog.getSaveFileName(
            self, 'Choose save location', None)[0]

    def arduGen(self):
        """
        Calls arducopter methods to create output files."""
        ardu.state(self.mi_file, self.tlog_file)
        ardu.auxiliary(self.mi_file, self.tlog_file, self.selected_gcs_loc)

        if(self.wpt_file):
            ardu.flight(self.mi_file, self.wpt_file, self.tlog_file)

        msgBox = QMessageBox.information(self, "Information", "Complete!")

    def djiGen(self):
        """Calls dji methods to create output files."""
        dji.state(self.mi_file, self.bin_file)
        dji.auxiliary(self.mi_file, self.bin_file, self.selected_gcs_loc)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Cleanlooks')
    gui = ConvGUI()
    sys.exit(app.exec_())
