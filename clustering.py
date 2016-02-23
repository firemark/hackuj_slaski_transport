#!/bin/env python2
import geojson
import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth
from numpy import array, unique
from sys import stderr

pred = lambda geo: geo['geometry']['type'] == u'LineString'

def make(filename, precision):
    with open(filename) as f:
        data = geojson.load(f)

    features = data['features']
    points = [
        geo['geometry']["coordinates"]
        for geo in features if pred(geo)
    ]
    ar_points = array(points).reshape(len(points) * 2, 2)
    bandwidth = estimate_bandwidth(ar_points) / precision
    cluster = MeanShift(bandwidth=bandwidth, n_jobs=-1)
    cluster.fit(ar_points)
    labels = cluster.labels_
    cluster_centers = cluster.cluster_centers_
    len_labels = len(unique(labels))
    stderr.write('clusters: %d\n' % len_labels)
    count_clusters = [
        np.sum(labels == i)
        for i in range(len_labels)
    ]
    points_geo = []

    for i, geo in enumerate(filter(pred, features)):
        local_labels = [labels[i*2 + j] for j in range(2)]
        old_points = geo['geometry']['coordinates']
        geo['geometry'] = geojson.LineString([
            list(cluster_centers[label])
            for label in local_labels
        ])
        if 'properties' not in geo:
           geo['properties'] = {} 
        geo['properties'].update(
            a_size=count_clusters[local_labels[0]],
            b_size=count_clusters[local_labels[1]],
            a_id=str(local_labels[0]),
            b_id=str(local_labels[1]),
        )
        points_geo += [
            {
                'geometry': geojson.Point(point),
                'properties': {'cluster_id': str(label)}
            }
            for point, label in zip(old_points, local_labels)
        ]

    features += points_geo
    return data

if __name__ == "__main__":
    from sys import argv, stdout
    filename = argv[1]
    prec = int(argv[2])
    data = make(filename, prec)
    geojson.dump(data, stdout)


