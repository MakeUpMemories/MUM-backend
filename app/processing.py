import sklearn.cluster as cluster
from PIL import Image, ImageDraw
import numpy as np


def process(img: Image):
    img.thumbnail((200, 200))
    data = np.array(img.getdata())
    least_clusters = None
    clusters = None
    for i in np.linspace(5, 7, 5):
        db = cluster.DBSCAN(eps=i, min_samples=10).fit(data)
        ln = len(set(db.labels_))
        if least_clusters is None or least_clusters > ln:
            least_clusters = ln
            clusters = db.labels_
            if least_clusters <= 7:
                break

    result = []
    for i in set(clusters):
        result.append(list(map(int, list(np.round(np.average(data[clusters == i], axis=0)))))) #govnokod
    return result


def compose_image(img: Image, colors, qrcode):
    palete = Image.new("RGB", (img.size[0], img.size[1] + 100))
    palete.paste(img)
    qrcode.thumbnail((100, 100))
    palete.paste(qrcode, (img.size[0] - 100, img.size[1]))
    draw = ImageDraw.Draw(palete)
    draw.rectangle(((0, img.size[1]), (img.size[0] - 100, img.size[1] + 100)), fill=(255, 255, 255))
    draw.text((10, img.size[1]), "MakeUp Memories", fill="black")
    delta = (img.size[0] - 100) / len(colors['colors'])
    for i in range(len(colors['colors'])):
        c = colors['colors'][i]
        draw.rectangle(((10 + delta * i, img.size[1] + 10), (5 + delta * (i + 1), img.size[1] + 90)), fill=(c[0], c[1], c[2]))
    return palete