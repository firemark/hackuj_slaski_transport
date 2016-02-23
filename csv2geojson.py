#!/bin/env python3
from csv import DictReader
from geojson import LineString, FeatureCollection, Feature

import json
import sys


def csv2collection(fp):
    reader = DictReader(fp, delimiter=';')
    data = [
        row2feature(row) for row in reader
    ]
    collection = FeatureCollection(data)
    return collection

def row2feature(row):
    p1 = [float(row['start lon']), float(row['start lat'])]
    p2 = [float(row['end lon']), float(row['end lat'])]
    vehicles_count = int(row['vehiclesCount'])

    line = LineString([p1, p2])
    properties = {'vehicles_count': vehicles_count}
    feature = Feature(geometry=line, properties=properties)

    return feature

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        with open(filename) as fp:
            collection = csv2collection(fp)
    else:
        collection = csv2collection(sys.stdin)
    json.dump(collection, sys.stdout)