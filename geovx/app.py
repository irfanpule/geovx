import csv

from PyQt5.QtWidgets import (
    QMainWindow, QAction, QFileDialog,
    QLineEdit, QLabel, QPushButton, QMessageBox, QDialog
)
from PyQt5.QtCore import QUrl
from PyQt5 import QtNetwork
from geovx.map_widget import QMapWidget
from geovx.utils import getPropertiesFeatures


class GeoVXMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.window_width, self.window_height = 1200, 800
        self.initUI()

        self.mapWidget = QMapWidget()
        self.setCentralWidget(self.mapWidget)
        self.inputWindow = InputURLWindow()
        self.setWindowTitle('GeoVX')
        self.setMinimumSize(self.window_width, self.window_height)
        self.geoJSONPath = ""
        self.geoJSONData = None

    def initUI(self):
        menubar = self.menuBar()

        inputMenu = menubar.addMenu('Input')
        geojsonFileMenu = QAction('Geojson from file', self)
        inputMenu.addAction(geojsonFileMenu)
        geojsonFileMenu.triggered.connect(self.importFile)

        geojsonUrlMenu = QAction('Geojson from url', self)
        inputMenu.addAction(geojsonUrlMenu)
        geojsonUrlMenu.triggered.connect(self.importFileURL)

        exportMenu = menubar.addMenu('Export')
        csvFileMenu = QAction('Properties Data to CSV', self)
        exportMenu.addAction(csvFileMenu)
        csvFileMenu.triggered.connect(self.exportTOCSV)

        aboutMenu = menubar.addMenu('Help')
        contactAction = QAction('Contact', self)
        aboutMenu.addAction(contactAction)
        contactAction.triggered.connect(self.showContact)
        aboutAction = QAction('About', self)
        aboutMenu.addAction(aboutAction)
        aboutAction.triggered.connect(self.showAbout)

    def importFile(self):
        self.geoJSONPath, _ = QFileDialog.getOpenFileName(filter="JSON files (*.json *.geojson)")
        if self.geoJSONPath and self.mapWidget.isValidGeojson(path=self.geoJSONPath):
            self.mapWidget.renderGeojsonData(path=self.geoJSONPath)

    def importFileURL(self):
        # example
        # https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/antarctic_ice_edge.json
        self.inputWindow.exec_()
        self.geoJSONPath = self.inputWindow.resultFromHandler
        if self.geoJSONPath and self.mapWidget.isValidGeojson(data=self.geoJSONPath):
            self.mapWidget.renderGeojsonData(data=self.geoJSONPath)

    def exportTOCSV(self):
        if not self.geoJSONPath and not self.geoJSONData:
            QMessageBox.critical(self, "Warning", "Data yet selected")
            return
        filename, _ = QFileDialog.getSaveFileName(self, 'Export CSV', '', 'CSV (*.csv)')
        features = getPropertiesFeatures(self.geoJSONPath, self.geoJSONData)
        if features:
            with open(filename, 'w', newline='') as csvfile:
                features_extract = []
                for feature in features:
                    properties = dict()
                    for key, value in feature['properties'].items():
                        properties[key] = value
                    features_extract.append(properties)

                fieldnames = list(features[0].get('properties').keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for data in features_extract:
                    writer.writerow(data)
            QMessageBox.critical(self, 'Success', "Success export data properties to csv")
            return
        else:
            QMessageBox.critical(self, "Warning", "This have't properties data")
            return

    def showAbout(self):
        aboutText = """
GeoVX is Geojson View and Export an application to display geojson data and export to shapefiles and csv
        """
        QMessageBox.about(self, 'About', aboutText)

    def showContact(self):
        aboutText = """
Email: irfan.pule@gmail.com
        """
        QMessageBox.about(self, 'About', aboutText)


class InputURLWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.window_width, self.window_height = 500, 150
        self.setMinimumSize(self.window_width, self.window_height)
        self.setWindowTitle("Input URL")

        textLabel = QLabel(self)
        textLabel.setText("Input your url")
        textLabel.move(20, 20)

        self.urlField = QLineEdit(self)
        self.urlField.move(20, 50)
        self.urlField.resize(460, 30)

        self.getButton = QPushButton('Get data', self)
        self.getButton.clicked.connect(self.doRequest)
        self.getButton.resize(460, 30)
        self.getButton.move(20, 90)

        self.resultFromHandler = None

    def doRequest(self):
        url = self.urlField.text()
        req = QtNetwork.QNetworkRequest(QUrl(url))
        self.manager = QtNetwork.QNetworkAccessManager()
        self.manager.finished.connect(self.handleResponse)
        self.manager.get(req)

    def handleResponse(self, reply):
        er = reply.error()
        if er == QtNetwork.QNetworkReply.NoError:
            bytes_string = reply.readAll()
            self.resultFromHandler = str(bytes_string, 'utf-8')
            self.close()
        else:
            QMessageBox.critical(self, "Warning", reply.errorString())
