import io
import folium
import json
from json.decoder import JSONDecodeError
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox


class QMapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.tiles = "cartodbpositron"

        # init map position
        map = folium.Map(
            tiles=self.tiles,
            location=(-0.789275, 113.921327),
            zoom_start=5,
        )

        data = io.BytesIO()
        map.save(data, close_file=False)
        self.webView = QWebEngineView()
        self.webView.setHtml(data.getvalue().decode())
        self.layout.addWidget(self.webView)

    def renderGeojsonData(self, path=None, data=None):
        # data from geojson
        if path and not data:
            file = open(path)
            try:
                data = json.load(file)
                features = data.get('features')
            except UnicodeDecodeError:
                pass
        else:
            try:
                data = json.loads(data)
                features = data.get('features')
            except JSONDecodeError:
                pass

        if features:
            properties = features[0].get('properties')
            geom = folium.GeoJson(data, name="geojson", popup=folium.GeoJsonPopup(fields=list(properties.keys())))
        else:
            geom = folium.GeoJson(data, name="geojson")

        map = folium.Map(tiles=self.tiles)
        map.fit_bounds(geom.get_bounds())
        geom.add_to(map)

        # save map data to data object
        data = io.BytesIO()
        map.save(data, close_file=False)
        self.webView.setHtml(data.getvalue().decode())
        self.layout.addWidget(self.webView)

    def isValidGeojson(self, path=None, data=None) -> bool:
        if path and not data:
            file = open(path)
            try:
                data = json.load(file)
            except UnicodeDecodeError:
                QMessageBox.critical(self, "Warning", "Can't decode this json")
                return False
        else:
            try:
                data = json.loads(data)
            except JSONDecodeError:
                QMessageBox.about(self, "Warning", "Response not json")
                return False

        try:
            type_map = data.get('type')
        except AttributeError:
            QMessageBox.critical(self, "Warning", "This structure invalid geojson")
            return False

        if not type_map:
            QMessageBox.critical(self, "Warning", "This structure invalid geojson")
            return False

        if type_map == 'FeatureCollection' or type_map == 'Feature':
            return True
        else:
            QMessageBox.critical(self, "Warning", "This structure invalid geojson")
            return True
