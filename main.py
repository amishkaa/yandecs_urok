import sys
from io import BytesIO
import requests
from PIL import Image
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import os


class Map(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("untitled.ui", self)

        self.geocoder_api_server = "http://geocode-maps.yandex.ru"
        self.delta = "0.005"
        self.geocode = "г. Калуга"
        self.toponym_coordinates = "37, 55"

        self.init()

    def load_map(self):
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": self.geocode,
            "ll": self.toponym_coordinates,
            "format": "json"
        }

        response = requests.get(geocoder_api_server, params=geocoder_params)

        # Преобразуем ответ в json-объект
        json_response = response.json()
        # Получаем первый топоним из ответа геокодера.
        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        # Координаты центра топонима:
        self.toponym_coordinates = toponym["Point"]["pos"]
        # Долгота и широта:
        toponym_longitude, toponym_lattitude = self.toponym_coordinates.split(" ")

        # Собираем параметры для запроса к StaticMapsAPI:
        map_params = {
            "ll": ",".join([toponym_longitude, toponym_lattitude]),
            "spn": ",".join([self.delta, self.delta]),
            "l": "map"
        }

        map_api_server = "http://static-maps.yandex.ru/1.x/"
        # ... и выполняем запрос
        response = requests.get(map_api_server, params=map_params)

        Image.open(BytesIO(
            response.content)).save("map.png")
        pixmap = QPixmap("map.png")
        self.map.setPixmap(pixmap)
        os.remove("map.png")

    def init(self):
        self.load_map()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0 and float(self.delta) > 0.00005:
            self.delta = str(float(self.delta) - float(self.delta) * 0.25)
        if event.angleDelta().y() < 0 and float(self.delta) < 20:
            self.delta = str(float(self.delta) + float(self.delta) * 0.25)

        self.load_map()

    def keyPressEvent(self, event):
        self.longitude = float(self.toponym_coordinates.split()[0])
        self.lattitude = float(self.toponym_coordinates.split()[1])
        if event.key() == Qt.Key_Up:
            print(1)
            self.lattitude += 0.05
        if event.key() == Qt.Key_Down:
            print(12)
            self.lattitude -= 0.05
        if event.key() == Qt.Key_Left:
            print(13)
            self.longitude -= 1
        if event.key() == Qt.Key_Right:
            print(4)
            self.longitude += 0.05

        print(self.longitude, self.lattitude)
        self.toponym_coordinates = f"{str(self.longitude)}, {str(self.lattitude)}"
        print(self.toponym_coordinates)
        self.load_map()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    map_app = Map()
    map_app.show()
    sys.exit(app.exec_())
