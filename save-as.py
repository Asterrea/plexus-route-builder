from __future__ import unicode_literals
from mongoengine import *
from shapely.geometry import mapping, LineString, asShape
from pathlib import Path
import json
from bson.json_util import dumps
from bson import json_util
import os
import fiona
from fiona import collection
from pymongo import MongoClient
import datetime

def db_connect(_MONGODB_USER=None, _MONGODB_PASSWD=None, _MONGODB_HOST=None,_MONGODB_PORT=None, _MONGODB_NAME=None):
    if not all((_MONGODB_USER, _MONGODB_PASSWD, _MONGODB_HOST, _MONGODB_PORT, _MONGODB_NAME)):
        _MONGODB_USER = 'heroku_zl9nqj92'
        _MONGODB_PASSWD = 'rrp1ea1fe1icl6obs18ldts7aa'
        _MONGODB_HOST = 'ds111489.mlab.com'
        _MONGODB_PORT = '11489'
        _MONGODB_NAME = 'heroku_zl9nqj92'
        _MONGODB_DATABASE_HOST = \
  'mongodb://%s:%s@%s:%s/%s' \
  % (_MONGODB_USER, _MONGODB_PASSWD, _MONGODB_HOST,_MONGODB_PORT, _MONGODB_NAME)

    client = MongoClient(_MONGODB_DATABASE_HOST)
    db = client.get_default_database()
    db.authenticate(_MONGODB_USER, _MONGODB_PASSWD)

    print("Connected to database.")
    
    return db, client

def db_to_geojson(db,client,collection='routes'):

    print("Collecting from DB to geojson.")
    
    if collection == 'routes':
        features = [r for r in db.routes.find()]
        geojson = {'type': 'FeatureCollection', 'features': features}
        geojson = json.loads(json.dumps(geojson, indent=4, default=json_util.default))
        print("Done.")
    
    return geojson
    
def save_as_geojson(filename, geojson, test=True):
    #geojson = json.loads(json.dumps(geojson, indent=4, default=json_util.default))
    #print(geojson['features'][0])
    try:
        if test is True:
            filepath = 'tests/%s.geojson' % filename
            check_if_path_exists(filepath)
            with open(filepath, 'w') as outfile:
                json.dump(geojson, outfile)
                print("Saved geojson file: dump")
        else:
            filepath = '%s.geojson' % filename
            with open(filepath, 'w') as outfile:
                json.dump(geojson, outfile)
                print("Saved geojson file: dumps")
    except ValueError as exc:
        if exc.errno != os.errno.EEXIST:
                raise
            
def save_as_shapefile(filepath,  geojson=True, csv=False):
    schema = {'geometry': 'LineString','properties': {'route_id': 'str'}}
                
    if geojson is True:
        now = datetime.date.today()
        outfilepath = 'files/{0}/{1}.shp'.format(str(now), str(now))
        check_if_path_exists(outfilepath)
        this_file = Path(filepath)
        print("Opening: " + str(this_file))
        with open(filepath,'r') as f:
            geojson2 = json.load(f)
        if this_file.is_file() and filepath.lower().endswith(('.geojson', '.json')):
            with fiona.open(outfilepath, "w", "ESRI Shapefile", schema) as outfile:
                test1 = geojson2.get("features")
                for r in test1:
                    rlinestring_shp = asShape(r['geometry'])
                    print(rlinestring_shp)
                    geom = mapping(rlinestring_shp)
                    print(geom)
                    outfile.write({
                        'properties': {
                            'route_id':r['route_id']
                        },
                        'geometry': geom
                    })
        print("Created Shapefiles")
                    
def check_if_path_exists(filepath):
    if not os.path.exists(os.path.dirname(filepath)):
        try:
            os.makedirs(os.path.dirname(filepath))
        except OSError as exc:
            if exc.errno != os.errno.EEXIST:
                raise
            
def test():
    
    db, client = db_connect()
    geojson = db_to_geojson(db,client)
    save_as_geojson('routes', geojson, test=False)
    save_as_shapefile('routes.geojson',geojson=True)

test()
