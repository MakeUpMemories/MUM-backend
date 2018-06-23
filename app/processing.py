import sklearn.cluster as cluster
from PIL import Image, ImageDraw
import functools

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


def image_transpose_exif(im):
    """
        Apply Image.transpose to ensure 0th row of pixels is at the visual
        top of the image, and 0th column is the visual left-hand side.
        Return the original image if unable to determine the orientation.

        As per CIPA DC-008-2012, the orientation field contains an integer,
        1 through 8. Other values are reserved.
    """

    exif_orientation_tag = 0x0112
    exif_transpose_sequences = [                   # Val  0th row  0th col
        [],                                        #  0    (reserved)
        [],                                        #  1   top      left
        [Image.FLIP_LEFT_RIGHT],                   #  2   top      right
        [Image.ROTATE_180],                        #  3   bottom   right
        [Image.FLIP_TOP_BOTTOM],                   #  4   bottom   left
        [Image.FLIP_LEFT_RIGHT, Image.ROTATE_90],  #  5   left     top
        [Image.ROTATE_270],                        #  6   right    top
        [Image.FLIP_TOP_BOTTOM, Image.ROTATE_90],  #  7   right    bottom
        [Image.ROTATE_90],                         #  8   left     bottom
    ]

    try:
        seq = exif_transpose_sequences[im._getexif()[exif_orientation_tag]]
    except Exception:
        return im
    else:
        return functools.reduce(type(im).transpose, seq, im)

def compose_image(img: Image, colors, qrcode):
    img = image_transpose_exif(img)
    img.thumbnail((800, 600))
    palete = Image.new("RGB", (img.size[0], img.size[1] + 100))
    palete.paste(img)
    qrcode.thumbnail((100, 100))
    palete.paste(qrcode, (img.size[0] - 100, img.size[1]))
    draw = ImageDraw.Draw(palete)
    draw.rectangle(((0, img.size[1]), (img.size[0] - 100, img.size[1] + 100)), fill=(255, 255, 255))
    delta = (img.size[0] - 100) / len(colors['colors'])
    for i in range(len(colors['colors'])):
        c = colors['colors'][i]
        draw.rectangle(((10 + delta * i, img.size[1] + 10), (5 + delta * (i + 1), img.size[1] + 90)), fill=(c[0], c[1], c[2]))
    return palete