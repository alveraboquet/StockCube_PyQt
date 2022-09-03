# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


import subprocess
import finnhub as fh
import yfinance as yf
import time
import datetime
import pytz
import os
import requests
import shutil
import sys
import zipfile
import io
from appdirs import *

OS = "Windows"
# OS = "MAC"

if OS == "Windows":
    import win32api

from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtCore import QDateTime, Qt, QTimer, QSortFilterProxyModel, QAbstractTableModel, QRect
from PyQt5.QtGui import *
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
                             QDial, QDialog, QFileDialog, QGridLayout, QGroupBox, QHBoxLayout, QInputDialog, QLabel,
                             QLineEdit, QMessageBox,
                             QProgressBar, QProgressDialog, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
                             QSlider, QSpinBox, QStyleFactory, QTableView, QTableWidget, QTableWidgetItem, QTabWidget,
                             QTextEdit,
                             QVBoxLayout, QWidget)

# app_directory='C:/Users/MattWatts/PycharmProjects/Test local dir/'

# from git import Repo

TextEntryHeight = 23


class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])


class WidgetGallery(QDialog):
    def __init__(self, parent=None):

        super(WidgetGallery, self).__init__(parent)
        self.currentAppVersion = 2.0

        if (OS == "Windows"):
            # Windows:
            try:
                results = subprocess.check_output(["netsh", "wlan", "show", "network"])
                print("check_output1 =>", results)
                results = results.decode("ascii")  # needed in python 3
                print("check_output2 =>", results)
            except:
                results = ''
            ls = results.split("\n")
            self.ssids = [v.strip() for k, v in (p.split(':') for p in ls if 'SSID' in p)]

            print("SSID =>", self.ssids)
            # file_path = os.path.dirname(os.path.realpath(__file__))

        else:
            scan_cmd = subprocess.Popen(
                ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-s"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            scan_out, scan_err = scan_cmd.communicate()
            try:
                results = scan_out.decode("ascii")  # needed in python 3
            except:
                results = ''
            ls = results.split("\n")[1:-1]
            self.ssids = []
            for each_line in ls:
                networkname = [e for e in each_line.split(" ") if e != ""][0]
                self.ssids.append(networkname)

            # file_path = os.path.join(os.environ['HOME'], 'StockCube')
            # if not os.path.isdir(file_path):
            #    os.mkdir(file_path)

        try:
            appname = "StockCube"
            appauthor = "StockCube"

            file_path = os.path.join(user_data_dir(appname))

            print("file_path =>", file_path)
            
            if not os.path.isdir(file_path):
                os.mkdir(file_path)

        except:
            file_path = self.choose_working_dir()

        self.findDongle()

        # Get working directory (this will default to app folder location once running local app)
        # file_path = app_directory
        # file_path = self.choose_working_dir()

        self.dir_location = file_path
        print("choose path =>", file_path)
        setup_loc = "Setup/"
        setup_path = os.path.join(file_path, setup_loc)
        setup_path = os.path.abspath(os.path.realpath(setup_path))
        valid_path = 0
        start_new_setup = 0
        print("setup_path =>", setup_path)
        if os.path.isdir(setup_path):
            valid_path = 1
            os.chdir(setup_path)
        else:
            os.mkdir(setup_path)
            os.chdir(setup_path)
            question = "No existing Setup found, do you want to load an existing setup from elsewhere?\n"
            reply = QMessageBox.question(self, 'Load existing Setup?', question)
            if reply == QMessageBox.No:
                msg = QMessageBox()
                msg.setWindowTitle("Continuing with new setup...")
                msg.setStandardButtons(QMessageBox.Ok)
                start_new_setup = 1
            if reply == QMessageBox.Yes:
                print("load_saved_setup =>", setup_path)
                self.load_saved_setup()

        sys.path.append("../../../")

        self.saved_network = False
        self.saved_api_key = False
        if start_new_setup == 0:
            try:
                with open("wifi.txt") as f:  # Open Wifi network file for reading
                    for line in f:  # iterate over each line
                        try:
                            saved_nw_name, saved_password, wifiCountry, wifikeyType, timezone, eol = line.split(";")
                            self.saved_nw_name = str(saved_nw_name)
                            self.saved_password = str(saved_password)
                            self.saved_country = str(wifiCountry)
                            self.saved_key_type = str(wifikeyType)
                            self.saved_timezone = str(timezone)
                            self.saved_network = True
                            self.complete_wifi_detail = True
                        except:  # Old setup file without country and key: force selection of country/key
                            saved_nw_name, saved_password, eol = line.split(";")
                            self.saved_nw_name = str(saved_nw_name)
                            self.saved_password = str(saved_password)
                            self.saved_country = "US: United States"
                            self.saved_key_type = "WPA-PSK"
                            self.saved_timezone = "Europe/London"
                            self.saved_network = True
                            self.complete_wifi_detail = False
                    f.close()
            except:
                self.saved_network = False
                question = "No valid setup found in this location. Would you like to load a saved setup?\n"
                reply = QMessageBox.question(self, 'Reload saved Setup?', question)
                if reply == QMessageBox.Yes:
                    self.load_saved_setup()
                if reply == QMessageBox.No:
                    msg = QMessageBox()
                    msg.setWindowTitle("Continuing with new setup...")
                    msg.setStandardButtons(QMessageBox.Ok)

            try:
                import fhapi
                self.saved_key = fhapi.APIkey
                self.saved_api_key = True
            except:
                self.saved_api_key = False

        try:
            with open(self.dongle_path + "/Setup/Version.py") as f:
                line = f.readline()  # Version just in first line - second line may or may not exist and is irrelevant
                versionName, currentVersion = line.split("=")
                print("USB dongle version = " + currentVersion + "\n")
        except:
            # No version information found on USB stick...
            currentVersion = 0.0

        self.currentCubeVersion = currentVersion

        self.originalPalette = QApplication.palette()

        disableWidgetsCheckBox = QCheckBox("&Disable widgets")
        self.available_tickers = ("None", "None")
        self.WLLabel = QLabel("Watchlist: ")
        self.PLabel = QLabel("Portfolio: ")
        self.exLabel = QLabel("Exchange list: ")
        self.createCompleteButton()
        self.createTopLeftGroupBox()
        self.createTopRightGroupBox()
        self.createBottomRightTabWidget()
        self.createBottomLeftGroupBox()

        disableWidgetsCheckBox.toggled.connect(self.topLeftGroupBox.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.topRightGroupBox.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.bottomRightTabWidget.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.bottomLeftGroupBox.setDisabled)

        topLayout = QGridLayout()
        if os.path.exists("GHVersion.py"):
            os.remove("GHVersion.py")
        github_available = 0
        try:
            # Version files will always have line 1 as the Stock Cube software version (Version=xxx\n)
            # Some (older ones) will then have a second line with app version - this becomes irrelevant now we release
            # formally through app stores (those systems will manage setup tool updates)
            url = "https://www.github.com/mmjwatts/ConvexSC/blob/main/Software/Version.py?raw=true"
            with open("GHVersion.py", "w") as f:
                print(requests.get(url).text, file=f)
            github_available = 1
        except:
            github_available = 0
        if github_available == 1:
            try:
                with open("GHVersion.py") as f:
                    line = f.readline()  # Version just in first line - second line may or may not exist and is irrelevant
                    versionName, githubVersion = line.split("=")
                    print("Github version = " + githubVersion + "\n")
                if (float(self.currentCubeVersion) < float(githubVersion)):
                    self.SWupdateButton = QPushButton("Stock Cube software \n update available!\n     Click here")
                    self.SWupdateButton.setStyleSheet("color: green; font: bold;")
                    topLayout.addWidget(self.SWupdateButton, 0, 0, 1, 2, Qt.AlignRight)
                else:
                    self.SWupdateButton = QPushButton("No Stock Cube software\n update available")
                    self.SWupdateButton.setStyleSheet("color: black")
                    topLayout.addWidget(self.SWupdateButton, 0, 0, 1, 1, Qt.AlignRight)
            except:
                github_available = 0
                self.SWupdateButton = QPushButton("Check for Stock Cube\nsoftware update")
                self.SWupdateButton.setStyleSheet("color: black")
                topLayout.addWidget(self.SWupdateButton, 0, 0, 1, 1, Qt.AlignRight)
        else:
            self.SWupdateButton = QPushButton("Check for Stock Cube\nsoftware update")
            self.SWupdateButton.setStyleSheet("color: black")
            topLayout.addWidget(self.SWupdateButton, 0, 0, 1, 1, Qt.AlignRight)
        loadSetupButton = QPushButton("Restore a saved setup")
        loadSetupButton.clicked.connect(lambda: self.load_setup_pressed())
        wifiEditButton = QPushButton("Edit Wifi / timezone")
        self.dongleButton = QPushButton("Find dongle")
        if (self.valid_dongle_path == 1):
            self.dongleLabel = QLabel("Setup dongle location: " + self.dongle_path)
            self.dongleLabel.setStyleSheet("color: green")
            self.dongleButton.setVisible(False)
        else:
            self.dongleLabel = QLabel("Can't find setup dongle")
            self.dongleLabel.setStyleSheet("color: red; font: bold;")
            self.dongleButton.setVisible(True)
        FHEditButton = QPushButton("Edit Finnhub.io API key")
        middleLabel = QLabel("Stock Cube display setup")

        topLayout.addWidget(wifiEditButton, 0, 0, 2, 1, Qt.AlignLeft)
        fhLayout = QHBoxLayout()
        fhLayout.addWidget(FHEditButton, 0, Qt.AlignLeft)

        wifiEditButton.clicked.connect(self.topLeftGroupBox.setDisabled)
        FHEditButton.clicked.connect(self.topRightGroupBox.setDisabled)
        self.SWupdateButton.clicked.connect(self.check_for_sw_update)
        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.topLeftGroupBox, 1, 0)
        mainLayout.addLayout(fhLayout, 2, 0, 1, 2)
        mainLayout.addWidget(self.topRightGroupBox, 3, 0)
        mainLayout.addWidget(middleLabel, 4, 0)
        mainLayout.addWidget(self.bottomRightTabWidget, 1, 1, 5, 1)
        mainLayout.addWidget(self.bottomLeftGroupBox, 5, 0)

        mainLayout.addWidget(self.completeButton, 6, 0, 2, 2, Qt.AlignLeft | Qt.AlignVCenter)
        self.completeButton.clicked.connect(self.saveSetup)
        mainLayout.addWidget(loadSetupButton, 6, 0, 2, 1, Qt.AlignRight | Qt.AlignVCenter)
        mainLayout.addWidget(self.dongleButton, 7, 1, 1, 1, Qt.AlignRight)
        self.dongleButton.clicked.connect(self.retryDongleSearch)
        mainLayout.addWidget(self.dongleLabel, 6, 1, Qt.AlignRight)
        mainLayout.addWidget(self.WLLabel, 6, 1, Qt.AlignLeft)
        mainLayout.addWidget(self.PLabel, 7, 1, Qt.AlignLeft)
        mainLayout.addWidget(self.exLabel, 8, 1, Qt.AlignLeft)
        mainLayout.setRowStretch(1, 0)
        mainLayout.setRowStretch(2, 0)
        mainLayout.setRowStretch(3, 0)
        mainLayout.setRowStretch(4, 0)
        mainLayout.setRowStretch(5, 1)
        mainLayout.setColumnStretch(0, 0)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("Stock Cube Setup Tool v" + str(self.currentAppVersion))

        self.changeStyle('Fusion')

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))
        self.changePalette()

    def createCompleteButton(self):
        self.completeButton = QPushButton("Save\n setup")
        self.completeButton.setStyleSheet("color: black; font: bold;")

    def changePalette(self):
        QApplication.setPalette(self.originalPalette)

    def createTopLeftGroupBox(self):

        self.topLeftGroupBox = QTabWidget()

        tab1 = QWidget()

        self.validWifi = 0
        self.wifiComboBox = QComboBox()
        self.wifiComboBox.addItem('')
        self.wifiComboBox.addItems(self.ssids)
        self.wifiComboBox.addItem('Enter manually...')
        wifiLabel = QLabel("&Select available Wifi network:")
        self.wifiInstrLabel = QLabel("")
        self.wifiNameLabel = QLabel("Please set using boxes above")
        self.blankLine = QLabel("")
        font = QFont("Arial", 9, italic=True)
        self.wifiNameLabel.setFont(font)
        wifiName = QLabel("Wifi network name:")
        wifiPWLabel = QLabel("Wifi password:")
        wifiLabel.setBuddy(self.wifiComboBox)
        self.wifiNameEdit = QLineEdit('')

        self.wifiNameEdit.setEchoMode(QLineEdit.Normal)
        self.wifiPWEdit = QLineEdit('')
        self.wifiPWEdit.setEchoMode(QLineEdit.Password)

        self.wifiCountrybox = QComboBox()
        self.country_codes = ["US: United States", "GB: United Kingdom", "NL: Netherlands", "CA: Canada", "IT: Italy",
                              "JP3: Japan", "DE: Germany", "PT: Portugal", "LU: Luxembourg", "NO: Norway",
                              "FI: Finland",
                              "DK: Denmark", "CH: Switzerland", "CZ: Czech Republic", "ES: Spain",
                              "KR: Republic of Korea (South Korea)", "CN: China", "FR: France", "HK: Hong Kong",
                              "SG: Singapore", "TW: Taiwan", "BR: Brazil", "IL: Israel", "SA: Saudi Arabia",
                              "LB: Lebanon",
                              "AE: United Arab Emirates", "ZA: South Africa", "AR: Argentina", "AU: Australia",
                              "AT: Austria", "BO: Bolivia", "CL: Chile", "GR: Greece", "IS: Iceland", "IN: India",
                              "IE: Ireland", "KW: Kuwait", "LI: Liechtenstein", "LT: Lithuania", "MX: Mexico",
                              "MA: Morocco",
                              "NZ: New Zealand", "PL: Poland", "PR: Puerto Rico", "SK: Slovak Republic", "SI: Slovenia",
                              "TH: Thailand", "UY: Uruguay", "PA: Panama", "RU: Russia", "EG: Egypt",
                              "TT: Trinidad and Tobago", "TR: Turkey", "CR: Costa Rica", "EC: Ecuador", "HN: Honduras",
                              "KE: Kenya", "UA: Ukraine", "VN: Vietnam", "BG: Bulgaria", "CY: Cyprus", "EE: Estonia",
                              "MU: Mauritius", "RO: Romania", "CS: Serbia and Montenegro", "ID: Indonesia", "PE: Peru",
                              "VE: Venezuela", "JM: Jamaica", "BH: Bahrain", "OM: Oman", "JO: Jordan", "BM: Bermuda",
                              "CO: Colombia", "DO: Dominican Republic", "GT: Guatemala", "PH: Philippines",
                              "LK: Sri Lanka",
                              "SV: El Salvador", "TN: Tunisia", "PK: Islamic Republic of Pakistan", "QA: Qatar"
            , "DZ: Algeria"]
        self.wifiCountrybox.addItems(self.country_codes)
        self.wifiCountrybox.setItemData(0, "Select the country code for your Wifi (usually just your country!)",
                                        Qt.ToolTipRole)
        self.wifikeybox = QComboBox()
        self.key_types = ["WPA-PSK", "WPA-EAP"]
        self.wifikeybox.addItems(self.key_types)
        wifiCountryLabel = QLabel("Wifi Country Code:")
        wifiKeyLabel = QLabel("Wifi passkey type (must be WPA/WPA2):")
        self.wifikeybox.setItemData(0, "NB: The Stock Cube only supports these two types of passkey management!",
                                    Qt.ToolTipRole)

        layout = QGridLayout()
        layout.addWidget(wifiLabel, 0, 0)
        layout.addWidget(self.wifiComboBox, 0, 1)
        self.wifiComboBox.currentTextChanged.connect(self.load_avail_wifi_name)
        layout.addWidget(self.wifiInstrLabel, 1, 0, Qt.AlignRight)
        layout.addWidget(self.wifiNameEdit, 1, 1)
        self.wifiNameEdit.setVisible(False)
        self.wifiButton2 = QPushButton("Use this network")
        self.wifiButton2.setVisible(False)
        layout.addWidget(self.wifiButton2, 1, 2)
        self.wifiButton2.clicked.connect(self.load_manual_wifi_name)
        layout.addWidget(wifiName, 2, 0, Qt.AlignRight)
        layout.addWidget(self.wifiNameLabel, 2, 1)
        layout.addWidget(wifiPWLabel, 3, 0, Qt.AlignRight)
        layout.addWidget(self.wifiPWEdit, 3, 1, 1, 1)
        self.wifiPWEdit.setMinimumWidth(200)
        layout.addWidget(self.blankLine, 4, 1)
        layout.addWidget(wifiCountryLabel, 5, 0, Qt.AlignRight)
        layout.addWidget(self.wifiCountrybox, 5, 1)
        layout.addWidget(wifiKeyLabel, 6, 0, Qt.AlignRight)
        layout.addWidget(self.wifikeybox, 6, 1)

        wifiDoneButton = QPushButton("Save")
        layout.addWidget(wifiDoneButton, 8, 1)
        wifiDoneButton.clicked.connect(self.save_wifi)

        tab1.setLayout(layout)

        tab2 = QWidget()

        timezoneLabel = QLabel("Select local timezone:")
        timezoneLabel2 = QLabel("Search timezones (filters list below)")
        timezoneLabel3 = QLabel("See here for details of timezones: "
                                "https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")
        timezoneLabel3.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.timezone = QComboBox()
        timezones = pytz.common_timezones
        self.timezone.addItems(timezones)

        timezone_list = list(timezones)
        row_count = len(timezone_list)
        model = QStandardItemModel(row_count, 1)
        # model.setHorizontalHeaderLabels(['Timezone'])

        for row, timezone in enumerate(timezone_list):
            item = QStandardItem(timezone)
            model.setItem(row, 0, item)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setFilterKeyColumn(-1)  # Search all columns.
        proxy_model.setSourceModel(model)
        proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        proxy_model.sort(0, Qt.AscendingOrder)

        self.tzList = QComboBox()
        searchbar = QLineEdit()

        self.tzList.setModel(proxy_model)
        searchbar.textChanged.connect(proxy_model.setFilterFixedString)
        self.localTimeLabel = QLabel(
            datetime.datetime.now(pytz.timezone(self.tzList.currentText())).strftime('%H:%M  %A %B %d, %Y'))
        self.localTimeLabel1 = QLabel("Current time & date in selected timezone:")

        self.tzList.currentTextChanged.connect(self.update_time)

        tab2box = QGridLayout()

        tab2box.addWidget(timezoneLabel3, 0, 0, 1, 3, Qt.AlignCenter)
        tab2box.addWidget(self.blankLine, 1, 1)
        tab2box.addWidget(timezoneLabel2, 2, 0, Qt.AlignRight)
        tab2box.addWidget(searchbar, 2, 1)

        tab2box.addWidget(timezoneLabel, 3, 0, Qt.AlignRight)
        tab2box.addWidget(self.tzList, 3, 1)
        tab2box.addWidget(self.blankLine, 4, 1)
        tab2box.addWidget(self.localTimeLabel1, 5, 0, Qt.AlignRight)
        tab2box.addWidget(self.localTimeLabel, 5, 1)
        self.localTimeLabel.setStyleSheet("color: black; font: bold;")
        tab2box.addWidget(self.blankLine, 6, 1)
        tab2.setLayout(tab2box)

        self.topLeftGroupBox.addTab(tab1, "Wifi")
        self.topLeftGroupBox.addTab(tab2, "Timezone")

        if self.saved_network:
            self.wifiNameLabel.setText(self.saved_nw_name)
            self.wifiPWEdit.setText(self.saved_password)
            self.wifiCountrybox.setCurrentText(self.saved_country)
            self.wifikeybox.setCurrentText(self.saved_key_type)
            self.tzList.setCurrentText(self.saved_timezone)
            self.update_time()
            if self.complete_wifi_detail:
                self.topLeftGroupBox.setDisabled(True)
                self.validWifi = 1
            QApplication.processEvents()

    def load_manual_wifi_name(self, text):
        self.wifiNameLabel.setText(self.wifiNameEdit.text())
        font = QFont("Arial", 9, italic=False)
        self.wifiNameLabel.setFont(font)
        QApplication.processEvents()

    def save_wifi(self):
        if self.wifiNameLabel.text() == "":
            self.validWifi = 0
            self.wifiNameLabel.setText('Please set using boxes above')
        else:
            self.topLeftGroupBox.setDisabled(True)
            fo = open("wifi.txt", "w")
            fo.write(self.wifiNameLabel.text() + ";" + self.wifiPWEdit.text() + ";" + self.wifiCountrybox.currentText()
                     + ";" + self.wifikeybox.currentText() + ";" + self.tzList.currentText() + ";\n")
            fo.close()
            self.validWifi = 1

    def load_avail_wifi_name(self, text):
        if text == 'Enter manually...':
            self.wifiInstrLabel.setText("Manual entry:")
            self.wifiNameEdit.setVisible(True)
            self.wifiButton2.setVisible(True)
            # self.wifiNameEdit.setDisabled(False)
            self.wifiNameEdit.setText('')
            self.wifiNameLabel.setText('Please set using boxes above')
            font = QFont("Arial", 9, italic=True)
            self.wifiNameLabel.setFont(font)
            QApplication.processEvents()
        else:
            if text == '':
                self.wifiInstrLabel.setText("")
                self.wifiNameEdit.setText('')
                self.wifiNameEdit.setVisible(False)
                self.wifiButton2.setVisible(False)
                self.wifiNameLabel.setText("Please set using boxes above")
                font = QFont("Arial", 9, italic=True)
                self.wifiNameLabel.setFont(font)
                QApplication.processEvents()
            else:
                self.wifiInstrLabel.setText("")
                self.wifiNameEdit.setText('')
                self.wifiNameEdit.setVisible(False)
                self.wifiButton2.setVisible(False)
                self.wifiNameLabel.setText(text)
                QApplication.processEvents()

    def check_for_sw_update(self, text):
        dir = "github"
        if os.path.exists("GHVersion.py"):
            os.remove("GHVersion.py")
        try:
            url = "https://www.github.com/mmjwatts/ConvexSC/blob/main/Software/Version.py?raw=true"
            with open("GHVersion.py", "w") as f:
                print(requests.get(url).text, file=f)
            github_available = 1
        except:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.Close)
            msg.setText("Error accessing Github. Check Wifi?")
            x = msg.exec_()
            github_available = 0
        if github_available == 1:
            try:
                with open("GHVersion.py") as f:
                    line = f.readline()  # Version just in first line - second line may or may not exist and is irrelevant
                    versionName, githubVersion = line.split("=")
                    print("Github version = " + githubVersion + "\n")
                if float(self.currentCubeVersion) < float(githubVersion):
                    question = "Cube software update available!\n" + "Current version = " + str(
                        self.currentCubeVersion) + "\n" + \
                               "New version = " + str(githubVersion) + "\n" + "Would you like to update?"
                    reply = QMessageBox.question(self, 'Software update', question)
                    if reply == QMessageBox.Yes:
                        print("updated dir =>", dir)
                        if os.path.exists(dir):
                            if os.path.exists(dir + "/.git"):
                                os.system('rmdir /S /Q "{}"'.format(dir + "/.git"))
                            shutil.rmtree(dir)
                        os.makedirs(dir)
                        
                        print("updated dir2 =>", dir)
                        msg = QDialog()
                        msg.setWindowTitle("Downloading new Stock Cube software. Please wait...")
                        msg.resize(750, 50)
                        x = msg.show()
                        url = "https://www.github.com/mmjwatts/ConvexSC/"
                        # Clones the git repo onto users local PC
                        # Repo.clone_from(url, dir, depth=1)
                        r = requests.get(
                            'https://raw.githubusercontent.com/mmjwatts/ConvexSC/main/Software/Software.zip',
                            stream=True)
                        z = zipfile.ZipFile(io.BytesIO(r.content))
                        z.extractall(dir)
                        try:
                            print("updated dongle_path =>", self.dongle_path)
                            dongle_dir = os.path.join(self.dongle_path, "Setup", "github")
                            dongle_dir = os.path.abspath(os.path.realpath(dongle_dir))
                            print("updated dongle_path22 =>", dongle_dir)
                            if os.path.exists(dongle_dir):
                                shutil.rmtree(dongle_dir)
                            # os.makedirs(dongle_dir)
                        except:
                            msg = QMessageBox()
                            msg.setWindowTitle("Could not find setup dongle")
                            msg.setStandardButtons(QMessageBox.Close)
                            msg.setText("Could not find your setup USB dongle!\n\n" + \
                                        "Please ensure your setup USB dongle is plugged in to this computer\n\n"
                                        "Use the \"Find USB dongle\" button at the bottom right to navigate to it\n\n")
                        if os.path.exists(dir):
                            shutil.copytree(dir, dongle_dir)
                            # os.system('rmdir /S /Q "{}"'.format(dir))  #This isn't working on MAC OS...
                            shutil.rmtree(dir)
                        x = msg.close()
                        msg = QMessageBox()
                        msg.setWindowTitle("Software update")
                        msg.setStandardButtons(QMessageBox.Ok)

                        msg.setText("Stock Cube software update downloaded!\n\n" +
                                    "Next time you plug in your setup USB stick to\n"
                                    "your Stock Cube, it will update itself!")
                        x = msg.exec_()
                        self.SWupdateButton.setText("Stock Cube software\nupdate downloaded")
                        self.SWupdateButton.setStyleSheet("color: black; font: bold;")
                    else:
                        msg = QMessageBox()
                        msg.setWindowTitle("Software update")
                        msg.setStandardButtons(QMessageBox.Close)
                        msg.setText("Stock Cube software update cancelled")
                        x = msg.exec_()
                else:
                    msg = QMessageBox()
                    msg.setWindowTitle("Software update")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.setText("Your Stock Cube software is up to date!")
                    x = msg.exec_()

            except Exception as e:
                msg = QMessageBox()
                msg.setWindowTitle("Error")
                msg.setStandardButtons(QMessageBox.Close)
                msg.setText("Error accessing Stock Cube software files. Please send "
                            "screenshot of this window to support@thestockcube.net\n\n" + "Error:\n" + str(e))
                x = msg.exec_()

    def createTopRightGroupBox(self):
        self.topRightGroupBox = QGroupBox(
            "Finnhub API setup (Sign up at https://finnhub.io/ - only need free API key!)")
        # self.topRightGroupBox.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.FHAPIEdit = QLineEdit('')
        self.FHAPIEdit.setEchoMode(QLineEdit.Normal)
        self.validAPI = 0
        self.FHAPIEdit.setMinimumWidth(200)
        self.FHAPILabel = QLabel("Enter your Finnhub.io API key:")
        # self.FHAPILabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.verifyLabel = QLabel("")
        saveAPIButton = QPushButton("Verify")
        saveAPIButton.setDefault(True)

        layout = QGridLayout()
        layout.addWidget(self.FHAPILabel, 0, 0)
        layout.addWidget(self.FHAPIEdit, 0, 1)
        layout.addWidget(saveAPIButton, 1, 1)
        layout.addWidget(self.verifyLabel, 1, 0)
        # layout.addStretch(1)
        self.topRightGroupBox.setLayout(layout)
        saveAPIButton.clicked.connect(self.save_api)

        if self.saved_api_key:
            self.FHAPIEdit.setText(self.saved_key)
            finnhub_client = fh.Client(api_key=self.FHAPIEdit.text())
            try:
                quote = finnhub_client.quote("AAPL")
                self.available_tickers = ("None", "None")
                self.topRightGroupBox.setDisabled(True)
                self.verifyLabel.setText("Freshly verified!")
                self.verifyLabel.setStyleSheet("color: green")
                self.validAPI = 1
            except:
                self.verifyLabel.setText("Invalid API key. Please try again")
                self.verifyLabel.setStyleSheet("color: red")
                self.validAPI = 0
            QApplication.processEvents()

    def save_api(self):
        finnhub_client = fh.Client(api_key=self.FHAPIEdit.text())
        try:
            quote = finnhub_client.quote("AAPL")
            self.topRightGroupBox.setDisabled(True)
            fo = open("fhapi.py", "w")
            fo.write("APIkey=\"" + self.FHAPIEdit.text() + "\"\n")
            fo.close()
            stock_tickers = finnhub_client.stock_symbols('US')
            print("stock_tickers1 =>", stock_tickers)
            self.available_tickers = list(map(lambda x: x["symbol"], stock_tickers))
            print("stock_tickers2 =>", self.available_tickers)
            self.available_tickers = sorted(self.available_tickers)
            print("stock_tickers3 =>", self.available_tickers)
            self.verifyLabel.setText("Verified!")
            self.verifyLabel.setStyleSheet("color: green")
            self.validAPI = 1
        except:
            self.verifyLabel.setText("Invalid API key. Please try again")
            self.verifyLabel.setStyleSheet("color: red")
            self.validAPI = 0
        QApplication.processEvents()

    def createBottomRightTabWidget(self):
        self.bottomRightTabWidget = QTabWidget()
        self.clearWLbutton = QPushButton("Clear all")
        self.saveWLbutton = QPushButton("Verify and save")
        self.clearPbutton = QPushButton("Clear all")
        self.savePbutton = QPushButton("Verify and save")
        self.clearExbutton = QPushButton("Clear all")
        self.saveExbutton = QPushButton("Verify and save")

        tab1 = QWidget()
        self.tableWidget = QTableWidget(12, 3)
        self.validPortfolio = 0
        self.validWL = 0
        self.stockOrcryptoComboBox = [QComboBox()] * 12
        self.cryptoComboBox = [QComboBox()] * 12
        self.ticker_price = [QLabel("")] * 12
        self.stockTicker = [QLineEdit('')] * 12
        self.ticker_list = [{'Type': 'Stock', 'Ticker': '', 'Price': ''} for _ in range(12)]
        self.crypto_tickers = ["", "1INCH", "AAVE", "ADA", "ALICE", "ANKR", "ARDR", "ARPA", "AVAX", "AXS",
                               "BAND", "BAT", "BCH", "BNB", "BTC", "BTT", "BUSD", "C98", "CAKE", "CHZ", "COMP",
                               "DENT", "DOGE", "DOT", "DYDX", "EGLD", "ENJ", "EOS", "ETC", "ETH", "FIL",
                               "FIO", "FTM", "GRT", "HBAR", "ICP", "IDEX", "IOTX", "LAZIO", "LINK", "LTC",
                               "LUNA", "MATIC", "MBOX", "MKR", "NEAR", "OMG", "PSG", "QNT", "QTUM", "RUNE",
                               "SAND", "SHIB", "SLP", "SNX", "SOL", "SXP", "THETA", "TLM", "TRU", "TRX",
                               "UNI", "USDC", "USDT", "VET", "WRX", "XLM", "XRP", "XTZ", "YFI", "ZEC", "ZIL"]

        self.tableWidget.setHorizontalHeaderLabels(["Type", "Ticker", "Price"])
        self.tableWidget.setColumnWidth(0, 150)
        self.tableWidget.setColumnWidth(1, 150)
        self.tableWidget.setColumnWidth(2, 100)

        # Initialise ticker_list as empty
        for x in range(0, 12):
            self.ticker_list[x]['Type'] = "Stock"
            self.ticker_list[x]['Ticker'] = ""
        # Populate ticker_list with saved list if exists
        try:
            num_tickers = 0
            with open("tickers.txt") as f:  # Open Wifi network file for reading
                for line in f:  # iterate over each line
                    self.ticker_list[num_tickers]['Type'], self.ticker_list[num_tickers]['Ticker'] = line.split()
                    saved_tickers = True
                    num_tickers = num_tickers + 1
                f.close()
                self.WLLabel.setText("Watchlist: Loaded existing watchlist - not saved any changes")
                self.WLLabel.setStyleSheet("color: orange")
                self.validWL = 1
            if num_tickers == 0:
                saved_tickers = False
                self.validWL = 0
                self.WLLabel.setText("Watchlist: Empty")
                self.WLLabel.setStyleSheet("color: red")
        except:
            saved_tickers = False
            self.validWL = 0
            self.WLLabel.setText("Watchlist: Empty")
            self.WLLabel.setStyleSheet("color: red")

        for x in range(0, 12):
            self.stockOrcryptoComboBox[x] = QComboBox()
            self.stockOrcryptoComboBox[x].addItem('NYSE stock')
            self.stockOrcryptoComboBox[x].addItem('Crypto')

            self.cryptoComboBox[x] = QComboBox()
            self.cryptoComboBox[x].addItems(self.crypto_tickers)
            self.stockTicker[x] = QLineEdit('')
            self.ticker_price[x] = QLabel("")
            self.ticker_price[x].setAlignment(Qt.AlignCenter)
            self.ticker_price[x].setDisabled(True)
            self.tableWidget.resizeRowToContents(x)
            self.tableWidget.setCellWidget(x, 0, self.stockOrcryptoComboBox[x])
            if saved_tickers:
                self.stockOrcryptoComboBox[x].setCurrentText(self.ticker_list[x]['Type'])
                if str(self.ticker_list[x]['Type']) == 'Stock':
                    self.stockTicker[x] = QLineEdit(self.ticker_list[x]['Ticker'])
                    self.tableWidget.setCellWidget(x, 1, self.stockTicker[x])
                else:
                    self.cryptoComboBox[x] = QComboBox()
                    self.cryptoComboBox[x].addItems(self.crypto_tickers)
                    self.cryptoComboBox[x].setCurrentText(self.ticker_list[x]['Ticker'])
                    self.tableWidget.setCellWidget(x, 1, self.cryptoComboBox[x])
            else:
                self.stockOrcryptoComboBox[x].setCurrentText('NYSE stock')
                self.ticker_list[x]['Type'] = "Stock"
                self.tableWidget.setCellWidget(x, 1, self.stockTicker[x])
            self.stockOrcryptoComboBox[x].currentTextChanged.connect(lambda index, num=x: self.typechange(index, num))
            self.tableWidget.setCellWidget(x, 2, self.ticker_price[x])

        w = self.tableWidget.verticalHeader().width()
        for i in range(self.tableWidget.columnCount()):
            w += self.tableWidget.columnWidth(i)
            h = self.tableWidget.horizontalHeader().height()
        for i in range(self.tableWidget.rowCount()):
            h += self.tableWidget.rowHeight(i)

        self.tableWidget.setMaximumSize(w, h)
        self.tableWidget.setMinimumSize(w, h)

        tab1hbox = QGridLayout()
        self.saveWLbutton.setGeometry(QRect(0, 0, 30, 30))
        self.clearWLbutton.setGeometry(QRect(0, 0, 30, 30))
        tab1hbox.addWidget(self.saveWLbutton, 0, 0, Qt.AlignLeft)
        tab1hbox.addWidget(self.clearWLbutton, 0, 0, Qt.AlignRight)
        tab1hbox.addWidget(self.tableWidget, 1, 0)
        tab1.setLayout(tab1hbox)
        self.saveWLbutton.clicked.connect(self.saveWLAll)
        self.clearWLbutton.clicked.connect(self.clearWLTickers)

        tab2 = QWidget()

        self.ptableWidget = QTableWidget(12, 6)

        self.pstockOrcryptoComboBox = [QComboBox()] * 12
        self.pcryptoComboBox = [QComboBox()] * 12
        self.pticker_quantity = [QLineEdit("")] * 12
        self.pticker_buyprice = [QLabel("")] * 12
        self.pticker_leverage = [QLineEdit("")] * 12
        self.pticker_price = [QLabel("")] * 12
        self.pticker_value = [QLabel("")] * 12
        self.pstockTicker = [QLineEdit('')] * 12
        self.pticker_list = [{'Type': 'Stock', 'Ticker': '', 'Quantity': '', 'BuyPrice': '', 'Leverage': ''} for _ in
                             range(12)]

        self.ptableWidget.setHorizontalHeaderLabels(
            ["Type", "Ticker", "Quantity", "Buy price ($)", "Leverage ratio (:1)", "Current value"])
        model = self.ptableWidget.model()
        default = self.ptableWidget.horizontalHeader().defaultAlignment()
        default |= Qt.TextWordWrap
        for col in range(self.ptableWidget.columnCount()):
            alignment = model.headerData(col, Qt.Horizontal, Qt.TextAlignmentRole)
            if alignment:
                alignment |= Qt.TextWordWrap
            else:
                alignment = default
            model.setHeaderData(
                col, Qt.Horizontal, alignment, Qt.TextAlignmentRole)
        # self.tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ptableWidget.setColumnWidth(0, 150)
        self.ptableWidget.setColumnWidth(1, 100)
        self.ptableWidget.setColumnWidth(2, 100)
        self.ptableWidget.setColumnWidth(3, 100)
        self.ptableWidget.setColumnWidth(4, 100)
        self.ptableWidget.setColumnWidth(5, 100)
        # Initialise ticker_list as empty
        for x in range(0, 12):
            # if str(self.stockOrcryptoComboBox[x].currentText()) == "NYSE stock":
            self.pticker_list[x]['Type'] = "Stock"
            self.pticker_list[x]['Ticker'] = ""
            self.pticker_list[x]['Quantity'] = ""
            self.pticker_list[x]['BuyPrice'] = ""
            self.pticker_list[x]['Leverage'] = "1"
        # Populate ticker_list with saved list if exists
        try:
            num_tickers = 0
            with open("portfolio.txt") as f:  # Open Wifi network file for reading
                for line in f:  # iterate over each line
                    self.pticker_list[num_tickers]['Type'], self.pticker_list[num_tickers]['Ticker'], \
                    self.pticker_list[num_tickers]['Quantity'], \
                    self.pticker_list[num_tickers]['BuyPrice'], self.pticker_list[num_tickers][
                        'Leverage'] = line.split()
                    saved_ptickers = True
                    num_tickers = num_tickers + 1
                f.close()
                self.PLabel.setText("Portfolio: Loaded existing portfolio - not saved any changes")
                self.PLabel.setStyleSheet("color: orange")
                self.validPortfolio = 1
            if num_tickers == 0:
                self.PLabel.setText("Portfolio: Empty")
                self.PLabel.setStyleSheet("color: red")
                saved_ptickers = False
                self.validPortfolio = 0

        except:
            saved_ptickers = False
            self.PLabel.setText("Portfolio: Empty")
            self.PLabel.setStyleSheet("color: red")
            self.validPortfolio = 0

        for x in range(0, 12):
            self.pstockOrcryptoComboBox[x] = QComboBox()
            self.pstockOrcryptoComboBox[x].addItem('NYSE stock')
            self.pstockOrcryptoComboBox[x].addItem('Crypto')
            self.pcryptoComboBox[x] = QComboBox()
            self.pcryptoComboBox[x].addItems(self.crypto_tickers)
            self.pstockTicker[x] = QLineEdit('')
            self.pticker_quantity[x] = QLineEdit('')
            self.pticker_buyprice[x] = QLineEdit('')
            self.pticker_leverage[x] = QLineEdit('1')
            self.pticker_value[x] = QLabel("")
            self.ptableWidget.resizeRowToContents(x)
            self.ptableWidget.setCellWidget(x, 0, self.pstockOrcryptoComboBox[x])
            if saved_ptickers:
                self.pstockOrcryptoComboBox[x].setCurrentText(self.pticker_list[x]['Type'])
                if str(self.pticker_list[x]['Type']) == 'Stock':
                    self.pstockTicker[x] = QLineEdit(self.pticker_list[x]['Ticker'])
                    self.ptableWidget.setCellWidget(x, 1, self.pstockTicker[x])
                else:
                    self.pcryptoComboBox[x] = QComboBox()
                    self.pcryptoComboBox[x].addItems(self.crypto_tickers)
                    self.pcryptoComboBox[x].setCurrentText(self.pticker_list[x]['Ticker'])
                    self.ptableWidget.setCellWidget(x, 1, self.pcryptoComboBox[x])
                self.pticker_quantity[x] = QLineEdit(self.pticker_list[x]['Quantity'])
                self.pticker_quantity[x].setAlignment(Qt.AlignCenter)
                self.pticker_buyprice[x] = QLineEdit(self.pticker_list[x]['BuyPrice'])
                self.pticker_buyprice[x].setAlignment(Qt.AlignCenter)
                self.pticker_leverage[x] = QLineEdit(self.pticker_list[x]['Leverage'])
                self.pticker_leverage[x].setAlignment(Qt.AlignCenter)
            else:
                self.pstockOrcryptoComboBox[x].setCurrentText('NYSE stock')
                self.pticker_list[x]['Type'] = "Stock"
                self.ptableWidget.setCellWidget(x, 1, self.pstockTicker[x])
            self.pstockOrcryptoComboBox[x].currentTextChanged.connect(lambda index, num=x: self.ptypechange(index, num))
            self.ptableWidget.setCellWidget(x, 2, self.pticker_quantity[x])
            self.ptableWidget.setCellWidget(x, 3, self.pticker_buyprice[x])
            self.ptableWidget.setCellWidget(x, 4, self.pticker_leverage[x])
            self.ptableWidget.setCellWidget(x, 5, self.pticker_value[x])

        self.ptableWidget.horizontalHeader().setFixedHeight(70)
        w = self.ptableWidget.verticalHeader().width()  # + 4  # +4 seems to be needed
        for i in range(self.ptableWidget.columnCount()):
            w += self.ptableWidget.columnWidth(i)  # seems to include gridline (on my machine)
            h = self.ptableWidget.horizontalHeader().height()  # + 4
        for i in range(self.ptableWidget.rowCount()):
            h += self.ptableWidget.rowHeight(i)

        self.ptableWidget.setMaximumSize(w, h)
        self.ptableWidget.setMinimumSize(w, h)

        tab2hbox = QGridLayout()
        self.savePbutton.setGeometry(QRect(0, 0, 30, 30))
        self.clearPbutton.setGeometry(QRect(0, 0, 30, 30))
        tab2hbox.addWidget(self.savePbutton, 0, 0, Qt.AlignLeft)
        tab2hbox.addWidget(self.clearPbutton, 0, 0, Qt.AlignRight)
        tab2hbox.addWidget(self.ptableWidget, 1, 0)
        tab2.setLayout(tab2hbox)
        self.savePbutton.clicked.connect(self.savePAll)
        self.clearPbutton.clicked.connect(self.clearPTickers)

        tab3 = QWidget()
        self.extableWidget = QTableWidget(5, 3)
        self.validEx = 0
        self.forexComboBox = [QComboBox()] * 5
        self.forexOrcryptoComboBox = [QComboBox()] * 5
        self.excryptoComboBox = [QComboBox()] * 5
        self.ex_price = [QLabel("")] * 5
        self.exch_list = [{'Type': 'Forex', 'Symbol': '', 'Price': ''} for _ in range(5)]
        self.forex_tickers = ["", "AUD", "EUR", "GBP", "NZD", "CAD", "CHF", "CNH", "HKD",
                              "JPY", "MXN", "TRY"]

        self.extableWidget.setHorizontalHeaderLabels(["Type", "Symbol", "Rate (USD)"])
        self.extableWidget.setColumnWidth(0, 150)
        self.extableWidget.setColumnWidth(1, 150)
        self.extableWidget.setColumnWidth(2, 100)

        # Initialise ticker_list as empty
        for x in range(0, 5):
            self.exch_list[x]['Type'] = ""
            self.exch_list[x]['Symbol'] = ""
            self.forexComboBox[x] = QComboBox()
            self.forexComboBox[x].addItems(self.forex_tickers)
            self.excryptoComboBox[x] = QComboBox()
            self.excryptoComboBox[x].addItems(self.crypto_tickers)
        # Populate ticker_list with saved list if exists
        try:
            num_tickers = 0
            with open("exchanges.txt") as f:  # Open Wifi network file for reading
                for line in f:  # iterate over each line
                    self.exch_list[num_tickers]['Type'], self.exch_list[num_tickers]['Symbol'] = line.split()
                    saved_exchanges = True
                    num_tickers = num_tickers + 1
                f.close()
                self.exLabel.setText("Forex/Crypto list: Loaded existing list - not saved any changes")
                self.exLabel.setStyleSheet("color: orange")
                self.validEx = 1
            if num_tickers == 0:
                saved_exchanges = False
                self.validEx = 0
                self.exLabel.setText("Forex/crypto list: Empty")
                self.exLabel.setStyleSheet("color: red")
        except:
            saved_exchanges = False
            self.validEx = 0
            self.exLabel.setText("Forex/crypto list: Empty")
            self.exLabel.setStyleSheet("color: red")

        for x in range(0, 5):
            self.forexOrcryptoComboBox[x] = QComboBox()
            self.forexOrcryptoComboBox[x].addItem('Forex')
            self.forexOrcryptoComboBox[x].addItem('Crypto')
            self.ex_price[x] = QLabel("")
            self.ex_price[x].setAlignment(Qt.AlignCenter)
            self.ex_price[x].setDisabled(True)
            self.extableWidget.resizeRowToContents(x)
            self.extableWidget.setCellWidget(x, 0, self.forexOrcryptoComboBox[x])
            if saved_exchanges and x < num_tickers:
                self.forexOrcryptoComboBox[x].setCurrentText(self.exch_list[x]['Type'])
                if str(self.exch_list[x]['Type']) == 'Forex':
                    self.forexComboBox[x] = QComboBox()
                    self.forexComboBox[x].addItems(self.forex_tickers)
                    self.forexComboBox[x].setCurrentText(self.exch_list[x]['Symbol'])
                    self.extableWidget.setCellWidget(x, 1, self.forexComboBox[x])
                else:
                    self.excryptoComboBox[x] = QComboBox()
                    self.excryptoComboBox[x].addItems(self.crypto_tickers)
                    self.excryptoComboBox[x].setCurrentText(self.exch_list[x]['Symbol'])
                    self.extableWidget.setCellWidget(x, 1, self.excryptoComboBox[x])
            else:
                self.forexOrcryptoComboBox[x].setCurrentText('Forex')
                self.exch_list[x]['Type'] = "Forex"
                self.extableWidget.setCellWidget(x, 1, self.forexComboBox[x])
            self.forexOrcryptoComboBox[x].currentTextChanged.connect(lambda index, num=x: self.extypechange(index, num))
            self.extableWidget.setCellWidget(x, 2, self.ex_price[x])

        w = self.extableWidget.verticalHeader().width()
        for i in range(self.extableWidget.columnCount()):
            w += self.extableWidget.columnWidth(i)
            h = self.extableWidget.horizontalHeader().height()
        for i in range(self.extableWidget.rowCount()):
            h += self.extableWidget.rowHeight(i)

        self.extableWidget.setMaximumSize(w, h)
        self.extableWidget.setMinimumSize(w, h)

        tab3hbox = QGridLayout()
        self.saveExbutton.setGeometry(QRect(0, 0, 30, 30))
        self.clearExbutton.setGeometry(QRect(0, 0, 30, 30))
        tab3hbox.addWidget(self.saveExbutton, 0, 0, Qt.AlignLeft)
        tab3hbox.addWidget(self.clearExbutton, 0, 0, Qt.AlignRight)
        tab3hbox.addWidget(self.extableWidget, 1, 0)
        tab3.setLayout(tab3hbox)
        self.saveExbutton.clicked.connect(self.saveExAll)
        self.clearExbutton.clicked.connect(self.clearExSymbols)

        tab4 = QWidget()

        self.tickerList = QTableView()
        self.searchbar = QLineEdit()

        self.tickerList.verticalHeader().setVisible(False)

        getListButton = QPushButton("Get available tickers")
        getListButton.clicked.connect(self.get_available_tickers)
        tab4box = QGridLayout()
        tab4box.addWidget(getListButton, 0, 0)
        tab4box.addWidget(self.searchbar, 1, 0)
        tab4box.addWidget(self.tickerList, 2, 0)

        tab4.setLayout(tab4box)

        tab5 = QWidget()
        workingLabel = QLabel("Directory where app is storing all your Setups:\n\n" + self.dir_location + "\n\n\n\n"
                                                                                                          "Please head to www.thestockcube.net/instructions for help\n\n"
                                                                                                          "Contact support@thestockcube.net if you are still having any issues "
                                                                                                          "with this Setup tool")

        tab5box = QGridLayout()
        tab5box.addWidget(workingLabel, 0, 0)
        tab5.setLayout(tab5box)

        workingLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.bottomRightTabWidget.addTab(tab1, "Stocks/Crypto Watchlist")
        self.bottomRightTabWidget.addTab(tab2, "Portfolio")
        self.bottomRightTabWidget.addTab(tab3, "Forex/crypto")
        self.bottomRightTabWidget.addTab(tab4, "Find ticker codes")
        self.bottomRightTabWidget.addTab(tab5, "Help")

    def get_available_tickers(self):
        finnhub_client = fh.Client(api_key=self.FHAPIEdit.text())
        try:
            stock_tickers = finnhub_client.stock_symbols('US')
            ticker_list = list(map(lambda x: x["symbol"], stock_tickers))
            name_list = list(map(lambda x: x["description"], stock_tickers))
            row_count = len(ticker_list)
            self.model = QStandardItemModel(row_count, 2)
            self.model.setHorizontalHeaderLabels(['Ticker', 'Name'])

            for row, ticker in enumerate(ticker_list):
                item = QStandardItem(ticker)
                self.model.setItem(row, 0, item)

            for row, tickername in enumerate(name_list):
                item = QStandardItem(tickername)
                self.model.setItem(row, 1, item)

            self.proxy_model = QSortFilterProxyModel()
            self.proxy_model.setFilterKeyColumn(-1)  # Search all columns.
            self.proxy_model.setSourceModel(self.model)
            self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
            self.proxy_model.sort(0, Qt.AscendingOrder)

            self.tickerList.setModel(self.proxy_model)
            self.tickerList.setColumnWidth(0, 100)
            self.tickerList.setColumnWidth(1, 400)
            # You can choose the type of search by connecting to a different slot here.
            # see https://doc.qt.io/qt-5/qsortfilterproxymodel.html#public-slots
            self.searchbar.textChanged.connect(self.proxy_model.setFilterFixedString)
        except:
            self.tickerList.setPlainText("Error getting tickers. Check API key?")

    def typechange(self, index, num):
        if str(index) == 'NYSE stock':
            self.stockTicker[num] = QLineEdit('')
            self.tableWidget.setCellWidget(num, 1, self.stockTicker[num])
        else:
            self.cryptoComboBox[num] = QComboBox()
            self.cryptoComboBox[num].addItems(self.crypto_tickers)
            self.tableWidget.setCellWidget(num, 1, self.cryptoComboBox[num])

    def ptypechange(self, index, num):
        if str(index) == 'NYSE stock':
            self.pstockTicker[num] = QLineEdit('')
            self.ptableWidget.setCellWidget(num, 1, self.pstockTicker[num])
        else:
            self.pcryptoComboBox[num] = QComboBox()
            self.pcryptoComboBox[num].addItems(self.crypto_tickers)
            self.ptableWidget.setCellWidget(num, 1, self.pcryptoComboBox[num])

    def extypechange(self, index, num):
        if str(index) == 'Forex':
            self.forexComboBox[num] = QComboBox()
            self.forexComboBox[num].addItems(self.forex_tickers)
            self.extableWidget.setCellWidget(num, 1, self.forexComboBox[num])
        else:
            self.excryptoComboBox[num] = QComboBox()
            self.excryptoComboBox[num].addItems(self.crypto_tickers)
            self.extableWidget.setCellWidget(num, 1, self.excryptoComboBox[num])

    def createBottomLeftGroupBox(self):
        self.bottomLeftGroupBox = QTabWidget()
        # self.bottomLeftGroupBox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Ignored)
        # QGroupBox("Stock Cube display setup")

        tab1 = QWidget()
        self.topFace1ComboBox = QComboBox()
        self.topFace1ComboBox.addItem("ETFs")
        self.topFace1ComboBox.setItemData(0, "Nasdaq 100 (QQQ), Dow Jones (DIA) and S&P 500 (SPY)", Qt.ToolTipRole)
        self.topFace1ComboBox.addItem("Portfolio performance")
        self.topFace1ComboBox.setItemData(1, "Daily and overall performance of your portfolio", Qt.ToolTipRole)
        self.topFace1ComboBox.addItem("Forex/crypto")
        self.topFace1ComboBox.setItemData(2, "Compact view of 5 Forex/Crypto rates", Qt.ToolTipRole)
        topFace1Label = QLabel("         Select top face display:")

        self.frontFace1ComboBox = QComboBox()
        self.frontFace1ComboBox.addItem("Watchlist")
        self.frontFace1ComboBox.setItemData(0, "Current price and daily change of up to 12 tickers (stocks or crypto)",
                                            Qt.ToolTipRole)
        self.frontFace1ComboBox.addItem("Portfolio detail")
        self.frontFace1ComboBox.setItemData(1,
                                            "Overall performance of each ticker in your portfolio since trade opened",
                                            Qt.ToolTipRole)
        self.frontFace1ComboBox.addItem("World Clock")
        self.frontFace1ComboBox.setItemData(2, "Local time and World clock (and NYSE open/closed status)",
                                            Qt.ToolTipRole)
        frontFace1Label = QLabel("Select front face display:")
        self.frontFace1ComboBox.currentTextChanged.connect(self.front_face_change1)

        brightness1Label = QLabel("Display brightness:   Min")
        self.brightness1maxLabel = QLabel("Max")
        self.slider1 = QSlider(Qt.Horizontal, self.bottomLeftGroupBox)
        self.slider1.setMaximum(70)
        self.slider1.setMinimum(31)
        self.slider1.setValue(70)
        self.slider1.setToolTip("Warning: displays may flicker occasionally if set to MAX brightness")

        self.scrollMode1 = QCheckBox()
        self.scrollLabel1 = QLabel("Scrolling tickers?")
        self.scrollMode1.setToolTip(
            "Scrolls all tickers in Watchlist/Portfolio. Otherwise statically shows the first 6")

        self.clockMode1 = QCheckBox()
        self.clockMode1Label = QLabel("Overlay small clock on front face:")
        self.clockMode1.setToolTip("Shows date and time at the bottom of front right display")

        self.nwMode1 = QCheckBox()
        self.nwMode1.setToolTip("Small status square on back corner of top display representing network status:\n"
                                " Green    = Wifi connected and all OK\n"
                                " Orange = Wifi connected but Cube time not synced over internet\n"
                                " Red       = Wifi not connected")
        nwMode1Label = QLabel("Show network status?")

        tab1box = QGridLayout()
        tab1box.addWidget(topFace1Label, 0, 0, Qt.AlignRight)
        tab1box.addWidget(self.topFace1ComboBox, 0, 1)
        tab1box.addWidget(self.nwMode1, 0, 2)
        tab1box.addWidget(nwMode1Label, 0, 3, Qt.AlignLeft)
        tab1box.addWidget(frontFace1Label, 2, 0, Qt.AlignRight)
        tab1box.addWidget(self.frontFace1ComboBox, 2, 1)
        tab1box.addWidget(self.scrollLabel1, 2, 3, Qt.AlignLeft)
        tab1box.addWidget(self.scrollMode1, 2, 2)
        tab1box.addWidget(self.clockMode1Label, 3, 0, Qt.AlignRight)
        tab1box.addWidget(self.clockMode1, 3, 1)
        tab1box.addWidget(brightness1Label, 4, 0, Qt.AlignRight)
        tab1box.addWidget(self.brightness1maxLabel, 4, 2, Qt.AlignLeft)
        tab1box.addWidget(self.slider1, 4, 1, 1, 1)

        tab1.setLayout(tab1box)

        # Default to ETFs and Watchlist for Mode 1
        self.topFace1ComboBox.setCurrentIndex(0)
        self.frontFace1ComboBox.setCurrentIndex(0)

        tab2 = QWidget()
        self.topFace2ComboBox = QComboBox()
        self.topFace2ComboBox.addItem("ETFs")
        self.topFace2ComboBox.setItemData(0, "Nasdaq 100 (QQQ), Dow Jones (DIA) and S&P 500 (SPY)", Qt.ToolTipRole)
        self.topFace2ComboBox.addItem("Portfolio performance")
        self.topFace2ComboBox.setItemData(1, "Daily and overall performance of your portfolio", Qt.ToolTipRole)
        self.topFace2ComboBox.addItem("Forex/crypto")
        self.topFace2ComboBox.setItemData(2, "Compact view of 5 Forex/Crypto rates", Qt.ToolTipRole)
        topFace2Label = QLabel("         Select top face display:")

        self.frontFace2ComboBox = QComboBox()
        self.frontFace2ComboBox.addItem("Watchlist")
        self.frontFace2ComboBox.setItemData(0, "Current price and daily change of up to 12 tickers (stocks or crypto)",
                                            Qt.ToolTipRole)
        self.frontFace2ComboBox.addItem("Portfolio detail")
        self.frontFace2ComboBox.setItemData(1,
                                            "Overall performance of each ticker in your portfolio since trade opened",
                                            Qt.ToolTipRole)
        self.frontFace2ComboBox.addItem("World Clock")
        self.frontFace2ComboBox.setItemData(2, "Local time and World clock (and NYSE open/closed status)",
                                            Qt.ToolTipRole)
        frontFace2Label = QLabel("Select front face display:")
        self.frontFace2ComboBox.currentTextChanged.connect(self.front_face_change2)

        brightness2Label = QLabel("Display brightness:   Min")
        brightness2maxLabel = QLabel("Max")
        self.slider2 = QSlider(Qt.Horizontal, self.bottomLeftGroupBox)
        self.slider2.setMaximum(70)
        self.slider2.setMinimum(31)
        self.slider2.setValue(70)
        self.slider2.setToolTip("Warning: displays may flicker occasionally if set to MAX brightness")

        self.clockMode2 = QCheckBox()
        self.clockMode2Label = QLabel("Overlay small clock on front face:")
        self.clockMode2.setToolTip("Shows date and time at the bottom of front right display")

        self.nwMode2 = QCheckBox()
        self.nwMode2.setToolTip("Small status square on back corner of top display representing network status:\n"
                                " Green    = Wifi connected and all OK\n"
                                " Orange = Wifi connected but Cube time not yet synced over internet\n"
                                " Red       = Wifi not connected")
        nwMode2Label = QLabel("Show network status?")

        self.scrollMode2 = QCheckBox()
        self.scrollLabel2 = QLabel("Scrolling tickers?")
        self.scrollMode2.setToolTip(
            "Scrolls all tickers in Watchlist/Portfolio. Otherwise statically shows the first 6")

        tab2box = QGridLayout()
        tab2box.addWidget(topFace2Label, 0, 0, Qt.AlignRight)
        tab2box.addWidget(self.topFace2ComboBox, 0, 1)
        tab2box.addWidget(self.nwMode2, 0, 2)
        tab2box.addWidget(nwMode2Label, 0, 3, Qt.AlignLeft)
        tab2box.addWidget(frontFace2Label, 2, 0, Qt.AlignRight)
        tab2box.addWidget(self.frontFace2ComboBox, 2, 1)
        tab2box.addWidget(self.scrollLabel2, 2, 3, Qt.AlignLeft)
        tab2box.addWidget(self.scrollMode2, 2, 2)
        tab2box.addWidget(self.clockMode2Label, 3, 0, Qt.AlignRight)
        tab2box.addWidget(self.clockMode2, 3, 1)
        tab2box.addWidget(brightness2Label, 4, 0, Qt.AlignRight)
        tab2box.addWidget(brightness2maxLabel, 4, 2, Qt.AlignLeft)
        tab2box.addWidget(self.slider2, 4, 1, 1, 1)

        tab2.setLayout(tab2box)

        # Default to Forex/Crypto and World clock for Mode 2
        self.topFace2ComboBox.setCurrentIndex(2)
        self.frontFace2ComboBox.setCurrentIndex(2)

        self.bottomLeftGroupBox.addTab(tab1, "Mode 1")
        self.bottomLeftGroupBox.addTab(tab2, "Mode 2")

        try:
            import mode1
            self.mode1Top = mode1.modeTop
            self.mode1Front = mode1.modeFront
            self.mode1brightness = mode1.modeBrightness
            self.topFace1ComboBox.setCurrentIndex(int(self.mode1Top))
            self.frontFace1ComboBox.setCurrentIndex(int(self.mode1Front))
            self.slider1.setValue(int(self.mode1brightness))
            try:
                if mode1.show_clock == 1:
                    self.clockMode1.setChecked(True)
                else:
                    self.clockMode1.setChecked(False)
                if mode1.nw_mode == 1:
                    self.nwMode1.setChecked(True)
                else:
                    self.nwMode1.setChecked(False)
                if mode1.scrolling == 1:
                    self.scrollMode1.setChecked(True)
                else:
                    self.scrollMode1.setChecked(False)
            except:
                self.clockMode1.setChecked(False)
                self.nwMode1.setChecked(False)
                self.scrollMode1.setChecked(True)  # Default to True
            if self.frontFace1ComboBox.currentText == 'World Clock':
                self.scrollMode1.setDisabled(True)
                self.scrollLabel1.setStyleSheet("color: grey")
                self.clockMode1.setDisabled(True)
                self.clockMode1Label.setStyleSheet("color: grey")
            else:
                self.scrollMode1.setDisabled(False)
                self.scrollLabel1.setStyleSheet("color: black")
                self.clockMode1.setDisabled(False)
                self.clockMode1Label.setStyleSheet("color: black")

            import mode2
            self.mode2Top = mode2.modeTop
            self.mode2Front = mode2.modeFront
            self.mode2brightness = mode2.modeBrightness
            self.topFace2ComboBox.setCurrentIndex(int(self.mode2Top))
            self.frontFace2ComboBox.setCurrentIndex(int(self.mode2Front))
            self.slider2.setValue(int(self.mode2brightness))
            try:
                if mode2.show_clock == 1:
                    self.clockMode2.setChecked(True)
                else:
                    self.clockMode2.setChecked(False)
                if mode2.nw_mode == 1:
                    self.nwMode2.setChecked(True)
                else:
                    self.nwMode2.setChecked(False)
                if mode2.scrolling == 1:
                    self.scrollMode2.setChecked(True)
                else:
                    self.scrollMode2.setChecked(False)
            except:
                self.clockMode2.setChecked(False)
                self.nwMode2.setChecked(False)
                self.scrollMode2.setChecked(True)
            if self.frontFace2ComboBox.currentText == 'World Clock':
                self.scrollMode2.setDisabled(True)
                self.scrollLabel2.setStyleSheet("color: grey")
                self.clockMode2.setDisabled(True)
                self.clockMode2Label.setStyleSheet("color: grey")
            else:
                self.scrollMode2.setDisabled(False)
                self.scrollLabel2.setStyleSheet("color: black")
                self.clockMode2.setDisabled(False)
                self.clockMode2Label.setStyleSheet("color: black")
            saved_modes = True
        except:
            saved_modes = False

    def front_face_change1(self, text):
        if text == 'World Clock':
            self.scrollMode1.setDisabled(True)
            self.scrollLabel1.setStyleSheet("color: grey")
            self.clockMode1.setDisabled(True)
            self.clockMode1Label.setStyleSheet("color: grey")
        else:
            self.scrollMode1.setDisabled(False)
            self.scrollLabel1.setStyleSheet("color: black")
            self.clockMode1.setDisabled(False)
            self.clockMode1Label.setStyleSheet("color: black")
        QApplication.processEvents()

    def front_face_change2(self, text):
        if text == 'World Clock':
            self.scrollMode2.setDisabled(True)
            self.scrollLabel2.setStyleSheet("color: grey")
            self.clockMode2.setDisabled(True)
            self.clockMode2Label.setStyleSheet("color: grey")
        else:
            self.scrollMode2.setDisabled(False)
            self.scrollLabel2.setStyleSheet("color: black")
            self.clockMode2.setDisabled(False)
            self.clockMode2Label.setStyleSheet("color: black")
        QApplication.processEvents()

    def findDongle(self):
        self.valid_dongle_path = 0
        if (OS == "Windows"):
            drives = win32api.GetLogicalDriveStrings()
            print("USB drives:", drives)
            dx = [x for x in drives.split("\000") if x]
            for drive in dx:
                try:
                    print("USB:", win32api.GetVolumeInformation(drive)[0])
                    if (win32api.GetVolumeInformation(drive)[0] == "SCSETUP"):
                        self.dongle_path = os.path.dirname(os.path.realpath(drive))
                        self.valid_dongle_path = 1
                        print("USB dongle:", self.dongle_path)
                except:
                    pass
        else:
            self.dongle_path = "/Volumes/SCSETUP/"
            if os.path.isdir(self.dongle_path):
                self.valid_dongle_path = 1
            else:
                self.valid_dongle_path = 0

    def retryDongleSearch(self):
        msg = QMessageBox()
        try:  # This catches if user presses cancel instead of setting new directory
            self.findDongle()
            if self.valid_dongle_path == 1:
                msg.setWindowTitle("Found setup dongle")
                msg.setStandardButtons(QMessageBox.Close)
                msg.setText("Setup dongle found!\n")
                x = msg.exec_()
                QApplication.processEvents()
                self.dongleLabel.setText("Setup dongle location: " + self.dongle_path)
                self.dongleLabel.setStyleSheet("color: green")
                self.dongleButton.setVisible(False)
                try:
                    with open(self.dongle_path + "/Setup/Version.py") as f:
                        line = f.readline()  # Version just in first line - second line may or may not exist and is irrelevant
                        versionName, currentVersion = line.split("=")
                        print("USB dongle version = " + currentVersion + "\n")
                        self.currentCubeVersion = currentVersion
                except:
                    # No version information found on USB stick...
                    currentVersion = 1.0
                    self.currentCubeVersion = currentVersion

            else:
                msg.setWindowTitle("Failed to find setup dongle")
                msg.setStandardButtons(QMessageBox.Close)
                msg.setText("Cannot find your Stock Cube setup dongle\n\n"
                            "Setup dongle MUST be a FAT32 formatted external USB stick, and named SCSETUP\n\n"
                            "This tool should find any external drive named SCSETUP\n\n"
                            "If you are having any problems, please contact support@thestockcube.net\n")
                x = msg.exec_()
                QApplication.processEvents()
                self.dongleLabel.setText("Can't find setup dongle")
                self.dongleLabel.setStyleSheet("color: red; font: bold;")
                self.dongleButton.setVisible(True)
        except:
            self.valid_dongle_path = 0

    def clearWLTickers(self):
        for x in range(0, 12):
            # if str(self.stockOrcryptoComboBox[x].currentText()) == "NYSE stock":
            self.ticker_list[x]['Type'] = "Stock"
            self.ticker_list[x]['Ticker'] = ""
            self.stockOrcryptoComboBox[x].setCurrentText('NYSE stock')
            self.stockTicker[x].setText("")
            self.tableWidget.setCellWidget(x, 1, self.stockTicker[x])
            self.ticker_price[x] = QLabel("")
            self.ticker_price[x].setStyleSheet("color: black")
            self.tableWidget.setCellWidget(x, 2, self.ticker_price[x])
        self.WLLabel.setText("Watchlist: Empty")
        self.WLLabel.setStyleSheet("color: red")
        self.validWL = 0

    def clearExSymbols(self):
        for x in range(0, 5):
            # if str(self.stockOrcryptoComboBox[x].currentText()) == "NYSE stock":
            self.exch_list[x]['Type'] = "Forex"
            self.exch_list[x]['Symbol'] = ""
            self.forexOrcryptoComboBox[x].setCurrentText('Forex')
            self.forexComboBox[x] = QComboBox()
            self.forexComboBox[x].addItems(self.forex_tickers)
            self.extableWidget.setCellWidget(x, 1, self.forexComboBox[x])
            self.ex_price[x] = QLabel("")
            self.ex_price[x].setStyleSheet("color: black")
            self.extableWidget.setCellWidget(x, 2, self.ex_price[x])
        self.exLabel.setText("Exchange list: Empty")
        self.exLabel.setStyleSheet("color: red")
        self.validEx = 0

    def clearPTickers(self):
        for x in range(0, 12):
            # if str(self.stockOrcryptoComboBox[x].currentText()) == "NYSE stock":
            self.pticker_list[x]['Type'] = "Stock"
            self.pticker_list[x]['Ticker'] = ""
            self.pstockOrcryptoComboBox[x].setCurrentText('NYSE stock')
            self.pstockTicker[x].setText("")
            self.pticker_quantity[x].setText("")
            self.pticker_buyprice[x].setText("")
            self.pticker_leverage[x].setText("1")
            self.pticker_value[x].setText("")
            self.ptableWidget.setCellWidget(x, 1, self.pstockTicker[x])
            self.ptableWidget.setCellWidget(x, 2, self.pticker_quantity[x])
            self.ptableWidget.setCellWidget(x, 3, self.pticker_buyprice[x])
            self.ptableWidget.setCellWidget(x, 4, self.pticker_leverage[x])
            self.ptableWidget.setCellWidget(x, 5, self.pticker_value[x])
        self.PLabel.setText("Portfolio: Empty")
        self.PLabel.setStyleSheet("color: red")
        self.validPortfolio = 0

    def saveWLAll(self):
        finnhub_client = fh.Client(api_key=self.FHAPIEdit.text())
        fo = open("tickers.txt", "w")
        self.validWL = 0
        for x in range(0, 12):
            if str(self.stockOrcryptoComboBox[x].currentText()) == "NYSE stock":
                self.ticker_list[x]['Type'] = "Stock"
                self.ticker_list[x]['Ticker'] = self.stockTicker[x].text().upper()
                if self.stockTicker[x].text() != "":
                    try:
                        quote = finnhub_client.quote(self.stockTicker[x].text().upper())
                        print("Quete =>", quote)
                        if quote['c'] != 0:
                            self.ticker_price[x] = QLabel(
                                "$" + "{0:.{1}f}".format(quote['c'], self.decimals(quote['c'])))
                            self.ticker_price[x].setStyleSheet("color: green")
                            self.tableWidget.setCellWidget(x, 2, self.ticker_price[x])
                            fo.write(self.ticker_list[x]['Type'] + " " + self.ticker_list[x]['Ticker'] + "\n")
                            self.validWL = 1
                        else:
                            self.ticker_price[x] = QLabel("Invalid ticker!")
                            self.ticker_price[x].setStyleSheet("color: red")
                            self.tableWidget.setCellWidget(x, 2, self.ticker_price[x])
                    except:
                        self.ticker_price[x] = QLabel("Invalid ticker!")
                        self.ticker_price[x].setStyleSheet("color: red")
                        self.tableWidget.setCellWidget(x, 2, self.ticker_price[x])

            else:
                if str(self.stockOrcryptoComboBox[x].currentText()) == "Crypto":
                    self.ticker_list[x]['Type'] = "Crypto"
                    self.ticker_list[x]['Ticker'] = self.cryptoComboBox[x].currentText()
                    if self.cryptoComboBox[x].currentText() != "":
                        try:
                            unix_timenow = int(time.time())
                            print("unix_time =>", unix_timenow)
                            quote = finnhub_client.crypto_candles(
                                str("BINANCE:" + self.cryptoComboBox[x].currentText() + "USDT"), '1', unix_timenow - 70,
                                unix_timenow - 10)
                            self.ticker_price[x] = QLabel(
                                "$" + "{0:.{1}f}".format(quote['c'][-1], self.decimals(quote['c'][-1])))
                            self.ticker_price[x].setStyleSheet("color: green")
                            self.tableWidget.setCellWidget(x, 2, self.ticker_price[x])
                            fo.write(self.ticker_list[x]['Type'] + " " + self.ticker_list[x]['Ticker'] + "\n")
                            self.validWL = 1
                        except:
                            self.ticker_price[x] = QLabel("Invalid ticker!")
                            self.ticker_price[x].setStyleSheet("color: red")
                            self.tableWidget.setCellWidget(x, 2, self.ticker_price[x])
                else:
                    self.ticker_list[x]['Type'] = "None"
        if self.validWL == 1:
            self.WLLabel.setText("Watchlist: Updated and saved")
            self.WLLabel.setStyleSheet("color: green")
        else:
            self.WLLabel.setText("Watchlist: Invalid / empty")
            self.WLLabel.setStyleSheet("color: red")
        QApplication.processEvents()

    def savePAll(self):
        finnhub_client = fh.Client(api_key=self.FHAPIEdit.text())
        fo = open("portfolio.txt", "w")
        self.validPortfolio = 0
        for x in range(0, 12):
            if str(self.pstockOrcryptoComboBox[x].currentText()) == "NYSE stock":
                self.pticker_list[x]['Type'] = "Stock"
                self.pticker_list[x]['Ticker'] = self.pstockTicker[x].text().upper()
                # print(self.pstockTicker[x].text() + "\n")
                self.pticker_list[x]['Quantity'] = self.pticker_quantity[x].text()
                # print(self.pticker_quantity[x].text() + "\n")
                self.pticker_list[x]['BuyPrice'] = self.pticker_buyprice[x].text()
                # print(self.pticker_buyprice[x].text() + "\n")
                self.pticker_list[x]['Leverage'] = self.pticker_leverage[x].text()
                # print(self.pticker_leverage[x].text() + "\n")
                if self.pstockTicker[x].text() != "":
                    try:
                        quote = finnhub_client.quote(self.pstockTicker[x].text().upper())
                        if quote['c'] != 0:
                            self.pticker_price[x] = (
                                        float(quote['c']) * float(self.pticker_list[x]['Quantity']) * float(
                                    self.pticker_list[x]['Leverage']))
                            self.pticker_price[x] = QLabel(
                                "$" + "{0:.{1}f}".format(self.pticker_price[x], self.decimals(self.pticker_price[x])))
                            self.pticker_price[x].setStyleSheet("color: green")
                            self.ptableWidget.setCellWidget(x, 5, self.pticker_price[x])
                            fo.write(self.pticker_list[x]['Type'] + " " + self.pticker_list[x]['Ticker'] + " " +
                                     self.pticker_list[x]['Quantity']
                                     + " " + self.pticker_list[x]['BuyPrice'] + " " + self.pticker_list[x][
                                         'Leverage'] + "\n")
                            self.validPortfolio = 1
                        else:
                            self.pticker_price[x] = QLabel("Invalid ticker!")
                            self.pticker_price[x].setStyleSheet("color: red")
                            self.ptableWidget.setCellWidget(x, 5, self.pticker_price[x])
                    except:
                        self.pticker_price[x] = QLabel("Invalid ticker!")
                        self.pticker_price[x].setStyleSheet("color: red")
                        self.ptableWidget.setCellWidget(x, 5, self.pticker_price[x])

            else:
                if str(self.pstockOrcryptoComboBox[x].currentText()) == "Crypto":
                    self.pticker_list[x]['Type'] = "Crypto"
                    self.pticker_list[x]['Ticker'] = self.pcryptoComboBox[x].currentText()
                    self.pticker_list[x]['Quantity'] = self.pticker_quantity[x].text()
                    self.pticker_list[x]['BuyPrice'] = self.pticker_buyprice[x].text()
                    self.pticker_list[x]['Leverage'] = self.pticker_leverage[x].text()
                    if self.pcryptoComboBox[x].currentText() != "":
                        try:
                            unix_timenow = int(time.time())
                            quote = finnhub_client.crypto_candles(
                                str("BINANCE:" + self.pcryptoComboBox[x].currentText() + "USDT"), '1',
                                unix_timenow - 70, unix_timenow - 10)
                            self.pticker_price[x] = (
                                        float(quote['c'][-1]) * float(self.pticker_list[x]['Quantity']) * float(
                                    self.pticker_list[x]['Leverage']))
                            self.pticker_price[x] = QLabel(
                                "$" + "{0:.{1}f}".format(self.pticker_price[x], self.decimals(self.pticker_price[x])))
                            self.pticker_price[x].setStyleSheet("color: green")
                            self.ptableWidget.setCellWidget(x, 5, self.pticker_price[x])
                            fo.write(self.pticker_list[x]['Type'] + " " + self.pticker_list[x]['Ticker'] + " " +
                                     self.pticker_list[x]['Quantity'] + " " + self.pticker_list[x]['BuyPrice'] + " " +
                                     self.pticker_list[x]['Leverage'] + "\n")
                            self.validPortfolio = 1
                        except:
                            self.pticker_price[x] = QLabel("Invalid ticker!")
                            self.pticker_price[x].setStyleSheet("color: red")
                            self.ptableWidget.setCellWidget(x, 5, self.pticker_price[x])
                else:
                    self.pticker_list[x]['Type'] = "None"
        if self.validPortfolio == 1:
            self.PLabel.setText("Portfolio: Updated and saved")
            self.PLabel.setStyleSheet("color: green")
        else:
            self.PLabel.setText("Portfolio: Empty / invalid")
            self.PLabel.setStyleSheet("color: red")

    def saveExAll(self):
        finnhub_client = fh.Client(api_key=self.FHAPIEdit.text())
        fo = open("exchanges.txt", "w")
        self.validEx = 0
        for x in range(0, 5):
            if str(self.forexOrcryptoComboBox[x].currentText()) == "Forex":
                self.exch_list[x]['Type'] = "Forex"
                self.exch_list[x]['Symbol'] = self.forexComboBox[x].currentText()
                if self.forexComboBox[x].currentText() != "":
                    try:
                        c = yf.Ticker(str(self.forexComboBox[x].currentText() + "USD=X"))
                        # Current live price uses period 1d and interval 1m and looks at latest Open:
                        print("YF_ticker11", c)
                        quote = c.history(period='1d', interval='1m')
                        print("YF_ticker22", quote)
                        # Daily change needs to grab today's open price, which is simply got from period='1d', interval='1d'
                        self.ex_price[x] = QLabel("$" + "{:.3f}".format(quote.Open[-1]))
                        self.ex_price[x].setAlignment(Qt.AlignCenter)
                        self.ex_price[x].setStyleSheet("color: green")
                        self.extableWidget.setCellWidget(x, 2, self.ex_price[x])
                        fo.write(self.exch_list[x]['Type'] + " " + self.exch_list[x]['Symbol'] + "\n")
                        self.validEx = 1
                    except:
                        self.ex_price[x] = QLabel("Invalid symbol!")
                        self.ex_price[x].setStyleSheet("color: red")
                        self.extableWidget.setCellWidget(x, 2, self.ex_price[x])
            else:
                if str(self.forexOrcryptoComboBox[x].currentText()) == "Crypto":
                    self.exch_list[x]['Type'] = "Crypto"
                    self.exch_list[x]['Symbol'] = self.excryptoComboBox[x].currentText()
                    if self.excryptoComboBox[x].currentText() != "":
                        try:
                            unix_timenow = int(time.time())
                            quote = finnhub_client.crypto_candles(
                                str("BINANCE:" + self.excryptoComboBox[x].currentText() + "USDT"), '1',
                                unix_timenow - 70, unix_timenow - 10)
                            self.ex_price[x] = QLabel(
                                "$" + "{0:.{1}f}".format(quote['c'][-1], self.decimals(quote['c'][-1])))
                            self.ex_price[x].setStyleSheet("color: green")
                            self.ex_price[x].setAlignment(Qt.AlignCenter)
                            self.extableWidget.setCellWidget(x, 2, self.ex_price[x])
                            fo.write(self.exch_list[x]['Type'] + " " + self.exch_list[x]['Symbol'] + "\n")
                            self.validEx = 1
                        except:
                            self.ex_price[x] = QLabel("Invalid symbol!")
                            self.ex_price[x].setStyleSheet("color: red")
                            self.extableWidget.setCellWidget(x, 2, "")
                else:
                    self.exch_list[x]['Type'] = "None"
        if self.validEx == 1:
            self.exLabel.setText("Exchange list: Updated and saved")
            self.exLabel.setStyleSheet("color: green")
        else:
            self.exLabel.setText("Exchange list: Invalid / empty")
            self.exLabel.setStyleSheet("color: red")
        QApplication.processEvents()

    def saveSetup(self):
        msg = QMessageBox()
        msg.setWindowTitle("Error with setup")
        msg.setStandardButtons(QMessageBox.Retry)
        msg.setIcon(QMessageBox.Critical)
        error = 0
        error_string = "Errors in setup as follows: \n"
        if self.validWifi == 0:
            error = 1
            error_string = error_string + "- Please check & save all Wifi and timezone information! \n"

        if self.validAPI == 0:
            error = 1
            error_string = error_string + "- No Finnhub API saved or verified: essential requirement! \n"

        if self.frontFace1ComboBox.currentIndex() == 0 or self.frontFace2ComboBox.currentIndex() == 0:
            if self.validWL == 0:
                error = 1
                error_string = error_string + "- No valid watchlist: can't save setup as your config requires one. \n"
                # msg.setText("No valid Watchlist! Can't save setup as your config requires one.")
                # x = msg.exec_()
        if self.topFace1ComboBox.currentIndex() == 1 or self.frontFace1ComboBox.currentIndex() == 1 \
                or self.topFace2ComboBox.currentIndex() == 1 or self.frontFace2ComboBox.currentIndex() == 1:
            if self.validPortfolio == 0:
                error = 1
                error_string = error_string + "- No valid portfolio: can't save setup as your config requires one. \n"

        if self.topFace1ComboBox.currentIndex() == 2 or self.topFace2ComboBox.currentIndex():
            if self.validEx == 0:
                error = 1
                error_string = error_string + "- No valid Forex/Crypto list: can't save setup as your config requires one. \n"

        if error == 0:
            fo = open("mode1.py", "w")
            if self.nwMode1.isChecked():
                nw_mode1 = 1
            else:
                nw_mode1 = 0
            if self.nwMode2.isChecked():
                nw_mode2 = 1
            else:
                nw_mode2 = 0
            if self.clockMode1.isChecked():
                clock_mode1 = 1
            else:
                clock_mode1 = 0
            if self.clockMode2.isChecked():
                clock_mode2 = 1
            else:
                clock_mode2 = 0
            if self.scrollMode1.isChecked():
                scroll_mode1 = 1
            else:
                scroll_mode1 = 0
            if self.scrollMode2.isChecked():
                scroll_mode2 = 1
            else:
                scroll_mode2 = 0
            fo.write("modeTop=" + str(self.topFace1ComboBox.currentIndex()) + "\nmodeFront=" + str(
                self.frontFace1ComboBox.currentIndex()) + "\nmodeBrightness=" + str(self.slider1.value()) +
                     "\nshow_clock=" + str(clock_mode1) + "\nnw_mode=" + str(nw_mode1) +
                     "\nscrolling=" + str(scroll_mode1))
            fo = open("mode2.py", "w")
            fo.write("modeTop=" + str(self.topFace2ComboBox.currentIndex()) + "\nmodeFront=" + str(
                self.frontFace2ComboBox.currentIndex()) + "\nmodeBrightness=" + str(self.slider2.value()) +
                     "\nshow_clock=" + str(clock_mode2) + "\nnw_mode=" + str(nw_mode2) +
                     "\nscrolling=" + str(scroll_mode2))

            # At this point in time, all setup files exist inside local PC directory
            # Now need to copy them to USB dongle, and also ask if user wants to save a copy of this setup for future use

            try:
                self.findDongle()  # Just makes sure dongle is still present
                if self.valid_dongle_path == 1:
                    # These are always present from a previous valid setup:
                    shutil.copyfile("./wifi.txt", self.dongle_path + "Setup/wifi.txt")
                    shutil.copyfile("./fhapi.py", self.dongle_path + "Setup/fhapi.py")
                    shutil.copyfile("./mode1.py", self.dongle_path + "Setup/mode1.py")
                    shutil.copyfile("./mode2.py", self.dongle_path + "Setup/mode2.py")
                    # The presence of these depends on the setup:
                    if os.path.exists("./exchanges.txt"):
                        shutil.copyfile("./exchanges.txt", self.dongle_path + "Setup/exchanges.txt")
                    if os.path.exists("./tickers.txt"):
                        shutil.copyfile("./tickers.txt", self.dongle_path + "Setup/tickers.txt")
                    if os.path.exists("./portfolio.txt"):
                        shutil.copyfile("./portfolio.txt", self.dongle_path + "Setup/portfolio.txt")
                else:
                    msg = QMessageBox()
                    msg.setWindowTitle("Setup NOT saved to dongle!")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.setText("No valid setup dongle has been found\n\n"
                                "Your setup is saved locally but you need to plug in a dongle and press save \n"
                                "again in order to upload it to your Stock Cube\n")
                    x = msg.exec_()
                # Ask user if they want to save a named copy of this Setup for later
                question = "Would you like to save a named copy of this Setup for future use?\n\n" \
                           "This is if you want quick reloading of different named setups later\n\n" \
                           "The current setup always gets reloaded by default the next time you run this tool"
                reply = QMessageBox.question(self, 'Save named copy of Setup?', question)
                if reply == QMessageBox.Yes:
                    save_name, ok = QInputDialog.getText(self, "Save setup", "Setup name:", QLineEdit.Normal, "")
                    save_dir = "../Setup_" + str(save_name)
                    save_this_setup = 1  # Used within existing name code below
                    if os.path.exists(save_dir):
                        question = "Setup name already exists. Do you want to overwrite it?\n"
                        reply = QMessageBox.question(self, 'Save name already exists', question)
                        if reply == QMessageBox.No:
                            save_this_setup = 0
                            msg = QMessageBox()
                            msg.setWindowTitle("Setup NOT saved locally")
                            msg.setStandardButtons(QMessageBox.Ok)
                            msg.setText("Did not save a named copy of this Setup...\n\n"
                                        "Your setup is saved to the setup dongle for use in your Stock Cube\n"
                                        "Press save again if you want to save a named copy of it locally for reloading later\n")
                            x = msg.exec_()
                        else:
                            os.rmdir(save_dir)
                    if save_this_setup == 1:
                        os.mkdir(save_dir)
                        # These are always present from a previous valid setup:
                        shutil.copyfile("./wifi.txt", save_dir + "/wifi.txt")
                        shutil.copyfile("./fhapi.py", save_dir + "/fhapi.py")
                        shutil.copyfile("./mode1.py", save_dir + "/mode1.py")
                        shutil.copyfile("./mode2.py", save_dir + "/mode2.py")
                        # The presence of these depends on the setup:
                        if os.path.exists("./exchanges.txt"):
                            shutil.copyfile("./exchanges.txt", save_dir + "/exchanges.txt")
                        if os.path.exists("./tickers.txt"):
                            shutil.copyfile("./tickers.txt", save_dir + "/tickers.txt")
                        if os.path.exists("./portfolio.txt"):
                            shutil.copyfile("./portfolio.txt", save_dir + "/portfolio.txt")

                if self.valid_dongle_path == 1:  # Only show this success box if valid dongle is here
                    msg = QMessageBox()
                    msg.setWindowTitle("Success!")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.setText("Stock Cube setup complete! \n\n"
                                "Please eject USB dongle and plug it into your Stock Cube")
                    x = msg.exec_()

            except Exception as e:
                msg = QMessageBox()
                msg.setWindowTitle("Could not save Setup!")
                msg.setStandardButtons(QMessageBox.Ok)
                error_string = error_string + "\n" + str(e)
                msg.setText("Couldn't save Setup...\n\n"
                            "I'm afraid there is a problem with saving your setup\n"
                            "The error reason is below:\n"
                            "Error: " + error_string + "\n\n"
                                                       "Please send a screenshot to support@thestockcube.net if you want any assistance")
                x = msg.exec_()

        else:
            error_string = error_string + "\nPlease send a screenshot to support@thestockcube.net if you need any support"
            msg.setText(error_string)
            x = msg.exec_()

    def decimals(self, v):
        if v > 1:
            return 2
        else:
            if v < 0.0001:
                return 6
            else:
                return 4

        # return max(0, min(5,5-int(math.log10(abs(v))))) if v else 5

    def findSetupFolder(self):
        msg = QMessageBox()
        msg.setWindowTitle("Setup folder not found")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setText("I'm having trouble finding your Stock Cube setup dongle (this MUST be named SCSETUP)\n"
                    "Please navigate to it using the popup window that is about to appear and all should be OK.")
        x = msg.exec_()
        return QFileDialog.getExistingDirectory(self, 'Please tell me where to find your setup dongle')

    def choose_working_dir(self):  # This will just be the Stock Cube app working directory once running local app
        msg = QMessageBox()
        msg.setWindowTitle("Choose working directory")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setText("Please choose the working directory for all of the app files\n\n"
                    "I tried to use this location, but failed:\n\n")
                    # + self.dir_location)
        x = msg.exec_()
        return QFileDialog.getExistingDirectory(self, 'Choose working directory')

    def update_time(self):
        self.localTimeLabel.setText(
            datetime.datetime.now(pytz.timezone(self.tzList.currentText())).strftime('%H:%M  %A %B %d, %Y'))

    def load_setup_pressed(self):
        question = "Would you like to port a saved setup?\n" \
                   "This will clear any Setup currently shown, so please make sure you've backed it up if needed\n"
        reply = QMessageBox.question(self, 'Port old Setup?', question)
        if reply == QMessageBox.Yes:
            self.load_saved_setup()
        if reply == QMessageBox.No:
            msg = QMessageBox()
            msg.setWindowTitle("Continuing with new setup...")
            msg.setStandardButtons(QMessageBox.Ok)

    def load_saved_setup(self):  # We MUST be in the local Setup folder before calling this function
        msg = QMessageBox()
        msg.setWindowTitle("Point me towards your saved Setup folder")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setText("Please navigate to your saved Setup folder in the window that appears next,\n"
                    "and I will grab your saved setup!")
        x = msg.exec_()
        savedSetupDir = QFileDialog.getExistingDirectory(self,
                                                         "Please tell me which saved Setup folder you'd like to load",
                                                         "../")
        try:
            # These are always present from a previous valid setup:
            shutil.copyfile(savedSetupDir + "/wifi.txt", "./wifi.txt")
            shutil.copyfile(savedSetupDir + "/fhapi.py", "./fhapi.py")
            shutil.copyfile(savedSetupDir + "/mode1.py", "./mode1.py")
            shutil.copyfile(savedSetupDir + "/mode2.py", "./mode2.py")
            # The presence of these depends on the setup:
            if os.path.exists(savedSetupDir + "/exchanges.txt"):  # Check there is at least a wifi.txt file
                shutil.copyfile(savedSetupDir + "/exchanges.txt", "./exchanges.txt")
            if os.path.exists(savedSetupDir + "/tickers.txt"):  # Check there is at least a wifi.txt file
                shutil.copyfile(savedSetupDir + "/tickers.txt", "./tickers.txt")
            if os.path.exists(savedSetupDir + "/portfolio.txt"):  # Check there is at least a wifi.txt file
                shutil.copyfile(savedSetupDir + "/portfolio.txt", "./portfolio.txt")
            msg = QMessageBox()
            msg.setWindowTitle("Loading of saved setup complete!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setText("Loading of your saved setup is complete. This app will now restart\n"
                        "and your saved setup will be loaded.")
            x = msg.exec_()
            os.execl(sys.executable, sys.executable, *sys.argv)
        except:
            msg = QMessageBox()
            msg.setWindowTitle("Could not find/copy saved Setup!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setText("Couldn't find old Setup files!\n\n"
                        "I'm afraid there is a problem with your proposed saved Setup folder\n"
                        "You will have to create a new one\n"
                        "Please contact support@thestockcube.net if you want any assistance")
            x = msg.exec_()


if __name__ == '__main__':
    appctxt = ApplicationContext()
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(appctxt.app.exec())