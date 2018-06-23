import sklearn.cluster as cluster
from PIL import Image
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
        result.append(list(np.round(np.average(data[clusters == i], axis=0))))
    return result
