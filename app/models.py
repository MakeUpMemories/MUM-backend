from flask.json import JSONEncoder
from typing import List
from enum import Enum
from PIL import Image

Color = List[int]


class ProductType(Enum):
    Foundation = "foundation"
    Cream = "cream"
    Moisturizer = "moisturizer"
    Blush = "blush"
    Concealer = "concealer"
    Face = "face"
    Primer = "primer"
    Powder = "powder"
    Correct = "correct"
    Contour = "contour"
    Highlight = "highlight"
    Lipstick = "lipstick"
    Liner = "liner"


class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, MUser):
            return {
                'login': obj._login,
                'email': obj._email,
            }
        elif isinstance(obj, MImage):
            return {
                'colors': obj._colors,
                'id': obj._id
            }
        elif isinstance(obj, Product) or isinstance(obj, IndividualProduct):
            return obj.to_json()
        elif isinstance(obj, Order):
            return {'img': obj._img, 'prd': list(map(lambda x: x.to_json(), obj._prd)), 'box': obj._box, 'price': obj._price}
        elif isinstance(obj, ProductType):
            return str(obj).split(".")[1]
        return super(MyJSONEncoder, self).default(obj)


class MUser:
    def __init__(self, login: str, email: str, password: str):
        self._login = login
        self._email = email
        self._password = password


class MImage:
    def __init__(self, image: Image, colors: List[Color], id: str):
        self._image = image
        self._colors = colors
        self._id = id


class Product:
    def __init__(self, type: ProductType, url: str, color: Color, name: str, price: float):
        self._type = type
        self._url = url
        self._color = color
        self._name = name
        self._price = price
        self._class = "Product"

    def to_json(self):
        return {'type': self._type, 'url': self._url, 'color': self._color, 'name': self._name, 'price': self._price}


class IndividualProduct(Product):
    def __init__(self, type: ProductType, url: str, color: Color, price: float, packaging: str):
        super(IndividualProduct, self).__init__(type, url, color, 'Individual ' + str(type).split(".")[1], price)
        self._class = 'IndividualProduct'
        self._packaging = packaging

    def to_json(self):
        d = super(IndividualProduct, self).to_json()
        d['packaging'] = self._packaging
        return d


class Order:
    def __init__(self, img: MImage, prd: List[Product], box: str, price: float):
        self._img = img
        self._prd = prd
        self._box = box
        self._price = price
