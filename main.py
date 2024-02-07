import sys
from io import BytesIO
import requests
from PIL import Image
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication
from PyQt5.QtGui import QPixmap
import os


class Map(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("untitled.ui", self)

        self.geocoder_api_server = "http://geocode-maps.yandex.ru"
        self.toponym_to_find = "г. Калуга"

        self.init()

    def load_map(self):
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": self.toponym_to_find,
            "format": "json"}

        response = requests.get(geocoder_api_server, params=geocoder_params)

        # Преобразуем ответ в json-объект
        json_response = response.json()
        # Получаем первый топоним из ответа геокодера.
        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        # Координаты центра топонима:
        toponym_coodrinates = toponym["Point"]["pos"]
        # Долгота и широта:
        toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

        delta = "0.005"

        # Собираем параметры для запроса к StaticMapsAPI:
        map_params = {
            "ll": ",".join([toponym_longitude, toponym_lattitude]),
            "spn": ",".join([delta, delta]),
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    map_app = Map()
    map_app.show()
    sys.exit(app.exec_())
