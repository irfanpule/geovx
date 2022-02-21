import json
from json.decoder import JSONDecodeError


def getPropertiesFeatures(path=None, data=None):
    # data from geojson
    if path and not data:
        file = open(path)
        try:
            data = json.load(file)
            features = data.get('features')
        except UnicodeDecodeError:
            pass
    else:
        try:
            data = json.loads(data)
            features = data.get('features')
        except JSONDecodeError:
            pass

    return features
