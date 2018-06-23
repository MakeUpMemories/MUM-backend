from PIL import Image
import logging
import qrcode
import uuid
import json
import os

from io import BytesIO
from flask import Flask, request, redirect, url_for, send_file, jsonify, abort, render_template
from werkzeug.utils import secure_filename

from app.models import MyJSONEncoder
import app.models as models
import app.processing as processing

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.json_encoder = MyJSONEncoder

UPLOAD_FOLDER = './files/'
ORDER_FOLDER = './orders/'

if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

if not os.path.exists(ORDER_FOLDER):
    os.mkdir(ORDER_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
print(app.config)
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


@app.route('/')
def main():
    imgs = []
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        if not file.endswith(".json"):
            imgs.append(file)
    return render_template('index.html', files=imgs)


@app.route('/user/register', methods=['POST'])
@app.route('/user/login', methods=['POST'])
def show_user_profile():
    return jsonify(models.MUser.from_json(request.json))


@app.route('/order/create', methods=['POST'])
def create_order():
    return jsonify(models.Order(
        id=uuid.uuid4(),
        img=None,
        prd=None,
        box=None,
        price=0))


@app.route('/order/finish', methods=['POST'])
def store_order():
    order = models.Order.from_json(request.json)
    with open(os.path.join(ORDER_FOLDER, order._id), 'w') as fp:
        json.dump(order.to_json(), fp)
    return jsonify(order)


@app.route('/order/<id>')
def get_order(id):
    pth = os.path.join(ORDER_FOLDER, id)
    if (os.path.exists(pth)):
        with open(os.path.join(ORDER_FOLDER, id), 'r') as fp:
            l = json.load(fp)
        print(l)
        return jsonify(l)
    else:
        abort(404)


@app.route('/order/<id>/qr')
def get_order_qr(id):
    return serve_pil_image(qrcode.make("http://18.184.165.57:8080/order/{}".format(id)))


@app.route('/uploads/<id>/qr')
def get_image_qr(id):
    return serve_pil_image(qrcode.make("http://18.184.165.57:8080/memory/{}".format(id)))


@app.route('/uploads/<id>/memory')
def compose(id):
    path = os.path.join(app.config['UPLOAD_FOLDER'], id)
    if (os.path.exists(path)):
        with open(path + ".json", "r") as fp:
            colors = json.load(fp)
        return serve_pil_image(processing.compose_image(Image.open(path), colors,
                                                        qrcode.make("http://18.184.165.57:8080/memory/{}".format(id))))

@app.route('/memory/<id>')
def imgtemplate(id):
    return render_template('ViewImage.html', id=id)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/image', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            i = models.MImage(id=filename, colors=processing.process(Image.open(path)))
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename + ".json"), 'w') as fp:
                json.dump(i.to_json(), fp)
            return  redirect("/memory/{}".format(i._id), code=302)

    return render_template("UploadImage.html")


from werkzeug.wsgi import SharedDataMiddleware

app.add_url_rule('/uploads/<filename>', 'uploaded_file',
                 build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploads': app.config['UPLOAD_FOLDER']
})


def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')
