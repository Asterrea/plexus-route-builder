from shapely.geometry import mapping, LineString, asShape
from pathlib import Path
import datetime
import os
import fiona
from fiona import collection
import json
from bson.json_util import dumps
from bson import json_util

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
                test1=geojson2
                print(test1["geometry"]["coordinates"])
                rlinestring_shp = asShape(test1['geometry'])
                print(rlinestring_shp)
                geom = mapping(rlinestring_shp)
                print(geom)
                outfile.write({
                    'properties': {
                        'route_id':test1['route_id']
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

save_as_shapefile('test-geometry.geojson', geojson=True)
