from pymongo import MongoClient
from functools import wraps
client = MongoClient()
import logging
import os

from flask import Flask, jsonify, request, Response, send_file
from app.models import MyJSONEncoder
import app.models as models

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.json_encoder = MyJSONEncoder

@app.route('/')
def main():
    return "/user to view User model (password field is omitted);\n /order to view Order model; \n /img to view Image model; \n /img/img to preview image"

@app.route('/user')
def show_user_profile():
    return jsonify(models.MUser(login="test", email="test@test.com", password="secretpass"))

@app.route('/order')
def show_order():
    return jsonify(models.Order(
        img="someid",
        prd=[
            models.Product(color=[0, 0, 0], name='Dat Lipstick', type=models.ProductType.Lipstick, url='http://google.com/', price=9.99),
            models.IndividualProduct(color=[0, 0, 0], type=models.ProductType.Lipstick, url='http://google.com/', price=9.99, packaging='matt'),
        ],
        box='exclusive',
        price=25))

@app.route('/img')
def show_image():
    return jsonify(models.MImage(image=None, id="imgid123", colors=[[0,0,0], [255, 255, 255], [10, 10, 10]]))


@app.route('/img/img')
def show_picture():
    return send_file(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', '1.jpg'))