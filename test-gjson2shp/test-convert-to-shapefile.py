from shapely.geometry import mapping, asShape
from pathlib import Path
from bson.json_util import dumps
from bson import json_util
from fiona import collection
import os
import json
import datetime

test = [{"geometry": {"type":"LineString", "coordinates":[[1,2],[3,4],[5,6]]},
        "route_id" : "ROUTE_880801",
        "_id":{"$oid":"5455969607b3t4456b"},
        "type":"Feature",
        "properties":{"route_name": "Recto"}
        },
        {"geometry": {"type":"LineString", "coordinates":[[1,2],[3,4],[5,6]]},
        "route_id" : "ROUTE_8801",
        "_id":{"$oid":"54554456b"},
        "type":"Feature",
        "properties":{"route_name": "Recto-Santolan"}
        }]

#print(test[0])

#print(test[0]['geometry'])

#rLinestring_shp = asShape(test[0]['geometry'])

#print(rLinestring_shp)
#print(rLinestring_shp.geom_type)
#print(rLinestring_shp.coords)
#print(list(rLinestring_shp.coords))

with open('/home/gridlockdev/Desktop/pythonidle/GTFS-GEOJSON/test-gjson2shp/test-geometry.geojson' ,'r') as f:
    geojson2 = json.load(f)   

print(type(geojson2))

#print(geojson.get('features'))

def save_as_shapefile(filepath,  geojson=True, csv=False):
    schema = {'geometry': 'LineString','properties': {'route_id': 'str'}}
                
    if geojson is True:
        now = datetime.date.today()
        outfilepath = 'files/{0}/{1}.shp'.format(str(now), str(now))
        check_if_path_exists(outfilepath)
        this_file = Path(filepath)
        if this_file.is_file() and filepath.lower().endswith(('.geojson', '.json')):
            with collection(outfilepath, "w", "ESRI Shapefile", schema) as outfile:
                #test1 = geojson2.get("features")
                geom = geojson2.get("geometry")
                print(geom)
                route_id = geojson2.get("route_id")
                print(route_id)
                rlinestring_shp = asShape(geom)
                print(rlinestring_shp)
                #for r in test1:
                #    rlinestring_shp = asShape(r['geometry'])
                outfile.write({
                    'properties': {
                        'route_id':route_id
                    },
                    'geometry': mapping(rlinestring_shp)
                 })


def check_if_path_exists(filepath):
    if not os.path.exists(os.path.dirname(filepath)):
        try:
            os.makedirs(os.path.dirname(filepath))
        except OSError as exc:
            if exc.errno != os.errno.EEXIST:
                raise

def align_route(rlinestring_shp):
    http://router.project-osrm.org/table/v1/driving/120.9834301,14.60350785;120.9924853,14.60077731;121.005038, 14.60173248;
    121.017, 14.6042; 121.026, 14.6105; 121.034, 14.6136; 121.043, 14.6185; 121.053, 14.6227; 121.065, 14.628; 121.073, 14.631; 121.086, 14.6223

    #kgcxAoqlaVLnBbAiK~Pee@oFiI`EuUsL}wBai@{k@}Ri{@kh@khAiJs^gg@arA}Dg]{Xyu@pDuKdy@sp@
    #http://router.project-osrm.org/route/v1/driving/120.9834301,14.60350785;121.086,14.6223
            
save_as_shapefile('/home/gridlockdev/Desktop/pythonidle/GTFS-GEOJSON/test-gjson2shp/test-geometry.geojson', geojson=True)
