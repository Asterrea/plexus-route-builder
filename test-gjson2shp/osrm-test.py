#import osrm
# -*- coding: utf-8 -*-
import numpy as np
from polyline.codec import PolylineCodec
from polyline import encode as polyline_encode
from pandas import DataFrame
try:
    from urllib.request import urlopen
except:
    from urllib2 import urlopen

try:
    from osgeo.ogr import Geometry
except:
    from ogr import Geometry

import json

def _chain(*lists):
    for li in lists:
        for elem in li:
            yield elem
            
def simple_route(coord_origin, coord_dest, coord_intermediate=None,
                 alternatives=False, steps=False, output="full",
                 geometry='geojson', overview="full", send_as_polyline=False):
    """
    Function wrapping OSRM 'viaroute' function and returning the JSON reponse
    with the route_geometry decoded (in WKT or WKB) if needed.

    Parameters
    ----------

    coord_origin : list/tuple of two floats
        (x ,y) where x is longitude and y is latitude
    coord_dest : list/tuple of two floats
        (x ,y) where x is longitude and y is latitude
    coord_intermediate : list of 2-floats list/tuple
        [(x ,y), (x, y), ...] where x is longitude and y is latitude
    alternatives : bool, optional
        Query (and resolve geometry if asked) for alternatives routes
        (default: False)
    output : str, optional
        Define the type of output (full response or only route(s)), default : "full".
    geometry : str, optional
        Format in which decode the geometry, either "polyline" (ie. not decoded),
        "geojson", "WKT" or "WKB" (default: "polyline").
    overview : str, optional
        Query for the geometry overview, either "simplified", "full" or "false"
        (Default: "simplified")
    url_config : osrm.RequestConfig, optional
        Parameters regarding the host, version and profile to use

    Returns
    -------
    result : dict
        The result, parsed as a dict, with the geometry decoded in the format
        defined in `geometry`.
    """
    host = 'http://router.project-osrm.org'
    
    if geometry.lower() not in ('wkt', 'well-known-text', 'text', 'polyline',
                                'wkb', 'well-known-binary', 'geojson'):
        raise ValueError("Invalid output format")
    else:
        geom_request = "geojson" if "geojson" in geometry.lower() \
            else "polyline"

    url = [host, '/route/v1/driving/', "{},{}".format(coord_origin[0], coord_origin[1]), ';']

    if coord_intermediate:
        url.append(";".join([','.join([str(i), str(j)]) for i, j in coord_intermediate]))

    url.extend([
        '{},{}'.format(coord_dest[0], coord_dest[1]),
        "?overview={}&steps={}&alternatives={}&geometries={}".format(
            overview, str(steps).lower(),
            str(alternatives).lower(), geom_request)
        ])
        
    rep = urlopen(''.join(url))
    parsed_json = json.loads(rep.read().decode('utf-8'))

    if "Ok" in parsed_json['code']:
        if geometry in ("polyline", "geojson") and output == "full":
            return parsed_json
        elif geometry in ("polyline", "geojson") and output == "routes":
            return parsed_json["routes"]

        return parsed_json if output == "full" else parsed_json["routes"]

    else:
        raise ValueError(
            'Error - OSRM status : {} \n Full json reponse : {}'.format(
                parsed_json['code'], parsed_json))

"""
Traverse routes geometry
"""
points= [(120.9834301, 14.60350785), (120.9924853, 14.60077731), (121.005038,14.60173248),
         (121.017, 14.6042), (121.026, 14.6105), (121.034, 14.6136),(121.043, 14.6185),
         (121.053, 14.6227), (121.065, 14.628), (121.073, 14.631), (121.086, 14.6223)]

#result= match(points, overview="simplified", geometry="geojson")
#print(result["matchings"][0]["geometry"])
"""
Re-route routes geometry and replace geometry
"""
result = simple_route(list(points[0]), list(points[-1]), output='route', overview='full', geometry="geojson")
print(result[0]["geometry"])

"""
Update Database
"""


