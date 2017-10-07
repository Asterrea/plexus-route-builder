# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson import BSON, decode_all
from pprint import pprint
from fiona import collection
from shapely.geometry import mapping, LineString, asShape
from random import randint
from pathlib import Path
from collections import OrderedDict
import json
import os,shutil,sys
import ast
import json
import csv

'''
Connect to mLab Database
Params:
mongodb_user, _password,_host,_port,_name
'''
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

    return db, client

def db_restore(collection_name, load_bson):
    with open(load_bson, 'rb') as f :
        collection_name.insert(decode_all(f.read()))
    
'''
Updates database with missing fields and values found in database
Params:
oid : objectid of database document
doc : document
db : database access
Return: None
'''
def update_route_rows(oid, doc, db):
    with open("routes.txt") as f:
        reader = csv.reader(f)
        header = reader.next()
        for line in reader:
            
            route_id = line[8]
            default_properties = ["agency_id", "route_name", "route_long", "route_desc", "route_type", "route_url", "route_tcolor"]
            idx = 0
            
            for item in default_properties:
                query = {"_id": ObjectId(oid)}
                
                if (doc["route_id"] == route_id):
                    default_val_pos = [line[0], line[1],line[2],line[3],line[4],line[5],line[7]]
                    update_val = '{ "$set":{"properties.%s": default_val_pos[%d] } }' % (item,idx)
                    db.routes.update(query, eval(update_val))
                if (idx < len(default_properties)):
                    idx+=1
                    
'''
Populate database from bson dump through restore
Params:
load_bson - latest overwritten bson file
db - database connection
'''
def populate_route_from(load_bson,db):
    db_restore(db.routes, load_bson)

'''
Default initialization of routes.
If routes are empty restore from routes.bson dump
Params:
db - database connection
'''
def initialize_default_fields(db):
    if "routes" in db.collection_names() and db.routes.count() > 0 :
        for document in db.routes.find():
            oid = document['_id']
            update_route_rows(oid,document,db)
    else:
        load_bson = 'dumps/routes.bson'
        populate_route_from(load_bson,db)
        
'''
Creates a unique 6 digit id pattern
Params:
n - number of digits
'''
def random_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

'''
Reads default gtfs text files and initialize them
in the database.
Params:
db - connection to mLab database
collection_name - target collection
'''
def insert_to_db(db,collection_name):
    trip_count = 0
    print (collection_name)
    filename = "%s.txt" % (collection_name)
    print (filename)
    with open(filename) as f:
        reader = csv.reader(f)
        header = reader.next()
        for line in reader:
            if(collection_name == "stops"):
                db.stops.insert(
                    {
                        "type":"Feature",
                        "stop_id": line[0],
                        "geometry":{
                            "type":"Point",
                            "coordinates":[line[5],line[4]]
                            },
                        "properties":{
                            "stop_code": line[1],
                            "stop_name": line[2],
                            "stop_desc": line[3],
                            "stop_url": line[7],
                            "zone_id": line[6],
                            "location_type": line[8],
                            "parent_station": line[9],
                            "wheelchair_boarding":line[10]
                            }
                    })
                    
            elif (collection_name == "calendar"):
                db.calendar.insert(
                    {
                        "service_id": line[0],
                        "properties": {
                            "start_date": line[8],
                            "end_date": line[9],
                            "operation":{
                                "monday" : line[1],
                                "tuesday": line[2],
                                "wednesday": line[3],
                                "thursday":line[4],
                                "friday":line[5],
                                "saturday":line[6],
                                "sunday":line[7]
                                }
                            }
                    })
            elif (collection_name == "trips"):
                
                OFF_SUN = [880893,882002]
                SAT = [881397,880853]
                SUN = [881614,881744,882006,881444,991445,881502]
                WE = [880774,881578,881579]
                WD = [881408, 880772, 881411, 880851]
                DAI = 724594
                
                query = "DAILY"
                if(line[1] in OFF_SUN): query = "OFF_SUNDAY"
                elif(line[1] in SAT): query = "SATURDAYS"
                elif(line[1] in SUN): query = "SUNDAYS"
                elif(line[1] in WE): query = "WEEKENDS"
                elif(line[1] in WD): query = "WEEKDAYS"
                
                cal_doc = db.calendar.find({"service_id": query})
                service_oid = ""
                for cursor in cal_doc:
                    service_oid = cursor["_id"]
                
                route_docs = db.routes.find({"route_id": line[0]})
                shape_id = ""
                for cursor in route_docs:
                    try:
                        shape_id = cursor["properties"]["shape_id"]
                    except KeyError:
                        #if (line[6] != ""):
                        #    db.routes.update({"_id": cursor["_id"]},{"$set":{"properties.shape_id": line[6]}})
                        #else:
                        generated_ids = []
                        randomid = 0
                        while(randomid == 0 or randomid in generated_ids):
                            randomid = random_N_digits(6)
                            print("random id:" + str(randomid))
                            if(randomid not in generated_ids):
                                generated_ids.append(randomid)
                                db.routes.update({"_id":cursor["_id"]},{"$set":{"properties.shape_id": randomid }})
                                test = db.routes.find({"_id":cursor["_id"]})
                                for cursor in test:
                                    shape_id = cursor["properties"]["shape_id"]
                                break
                            else:
                                print("In randomId already")

                db.trips.insert(
                    {
                        "trip_id":line[7],
                        "properties" : {
                        "trip_short_name": line[2],
                        "trip_headsign":line[3],
                        "trip_direction_id":line[4],
                        "trip_block_id":line[5],
                        "service_id": service_oid,
                        "route_id" : line[0],
                        "shape_id" : shape_id
                        }
                    })
                
            elif (collection_name == "frequencies"):
                trip = db.trips.find({"trip_id":line[0]})
                for cursor in trip:
                    db.trips.update(
                        {"_id": cursor["_id"]},
                        {"$set":
                             {
                             "properties.start_time": line[1],
                             "properties.end_time": line[2],
                             "properties.headway_secs": line[3],
                             "properties.exact_times": line[4]
                             }
                        })
            elif (collection_name == "stop_times"):
                trip = db.trips.find({"trip_id":line[0]})
                trip_count =trip_count+1
                print(trip_count)
                for cursor in trip:
                    print("%s Pushing stop_times data to: %s") % (line[2], cursor["properties"]["route_id"])
                    db.trips.update(
                        {"_id":cursor["_id"]},
                        {"$push":
                            {
                                "stop_times": {"seq":line[1],"stop_id":line[2],"arrival_time":line[3], "departure_time":line[4],
                                            "stop_headsign":line[5], "pickup_type":line[6], "drop_off_type":line[7],
                                            "shape_dist_traveled":line[8]
                                            }
                            }
                        })

def strip_non_asciii(item):
    stripped = (c for c in item if 0< ord(c) <127)
    return ''.join(stripped)

def build_agency(db,to_directory, filename):
    filepath = os.path.join(to_directory,filename)
    print(filepath)
    with open(filepath, 'wb') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["agency_id", "agency_name", "agency_url",
                                                     "agency_timezone","agency_lang","agency_phone"])
        writer.writeheader()
        
        agencies = db.agency.find()
        for agency in agencies:
            writer.writerow({"agency_id": agency["agency_id"], "agency_name": agency["agency_name"],
                              "agency_url":agency["properties"]["agency_url"], "agency_timezone":agency["properties"]["agency_timezone"],
                              "agency_lang":agency["properties"]["agency_lang"], "agency_phone":agency["properties"]["agency_phone"]})

        outfile.close()
        
def build_calendar(db,to_directory, filename):
    filepath = os.path.join(to_directory,filename)
    print(filepath)
    with open(filepath, 'wb') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["service_id","monday","tuesday","wednesday","thursday",
                                                     "friday","saturday","sunday","start_date","end_date"], extrasaction = 'ignore')
        writer.writeheader()
        
        calendar = db.calendar.find()
        for days in calendar:
            writer.writerow({"service_id":days["service_id"],"monday":days["properties"]["operation"]["monday"],
                              "tuesday": days["properties"]["operation"]["tuesday"],"wednesday":days["properties"]["operation"]["wednesday"],
                              "thursday":days["properties"]["operation"]["thursday"],"friday":days["properties"]["operation"]["friday"],
                              "saturday":days["properties"]["operation"]["saturday"],"sunday":days["properties"]["operation"]["sunday"],
                              "start_date":days["properties"]["start_date"], "end_date":days["properties"]["end_date"]})
        outfile.close()
        
def build_feed_info(db,to_directory, filename):
    filepath = os.path.join(to_directory,filename)
    print(filepath)
    field_dict = OrderedDict([("feed_publisher_name", "Plexus"), ("feed_publisher_url","https://theis-plexus.herokuapp.com"), ("feed_lang","en")])
    with open(filepath, 'wb') as outfile:
        writer = csv.DictWriter(outfile, field_dict.keys())
        writer.writeheader()
        writer.writerow(field_dict)
        outfile.close()
                                
def build_frequencies(db,to_directory, filename):
    filepath = os.path.join(to_directory,filename)
    print(filepath)
    with open(filepath, 'wb') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["trip_id","start_time","end_time","headway_secs","exact_times"])
        writer.writeheader()
        
        trips = db.trips.find()
        for trip in trips:
            writer.writerow({"trip_id": trip["trip_id"], "start_time":trip["properties"]["start_time"], "end_time":trip["properties"]["end_time"],
                             "headway_secs":trip["properties"]["headway_secs"], "exact_times":trip["properties"]["exact_times"]})
        outfile.close()
        
def build_routes(db,to_directory, filename):
    filepath = os.path.join(to_directory,filename)
    print(filepath)
    with open(filepath, 'wb') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["route_id", "agency_id","route_short_name","route_long_name","route_desc","route_type",
                                                     "route_url","route_color","route_text_color"], extrasaction = 'ignore', quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        
        routes = db.routes.find()
        for route in routes:
            try:
                route_color = route["properties"]["route_color"]
                route_tcolor = route["properties"]["route_tcolor"]
            except KeyError:
                route_color = "#0000FF"
                route_tcolor = ""

            try:
                route["properties"]["agency_id"]
            except KeyError:
                print("Error at route properties!" + str(route["route_id"]))
                continue;    
            writer.writerow({"route_id":strip_non_asciii(route["route_id"]),"agency_id":strip_non_asciii(route["properties"]["agency_id"]),
                             "route_short_name": strip_non_asciii(route["properties"]["route_name"]),"route_long_name":strip_non_asciii(route["properties"]["route_long"]),
                             "route_desc":strip_non_asciii(route["properties"]["route_desc"]),"route_type":strip_non_asciii(route["properties"]["route_type"]),
                             "route_url":strip_non_asciii(route["properties"]["route_url"]),"route_color":strip_non_asciii(route_color),"route_text_color":strip_non_asciii(route_tcolor)})
    outfile.close()
       
def build_shapes(db,to_directory, filename):
    filepath = os.path.join(to_directory,filename)
    print(filepath)
    with open(filepath, 'wb') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["shape_id","shape_pt_sequence","shape_dist_traveled","shape_pt_lat","shape_pt_lon"], extrasaction = 'ignore')
        writer.writeheader()
        
        routes = db.routes.find()
        for route in routes:
            print("SHAPE FOR:" + str(route["route_id"]))
            count=0
            for item in route["geometry"]["coordinates"]:
                count += 1
                writer.writerow({"shape_id": route["properties"]["shape_id"],"shape_pt_sequence": count,"shape_dist_traveled": "" ,"shape_pt_lat" : item[1],"shape_pt_lon": item[0]})
        outfile.close()
        
def build_stops(db,to_directory, filename):
    filepath = os.path.join(to_directory,filename)
    print(filepath)
    with open(filepath, 'wb') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["stop_id","stop_code","stop_name","stop_desc","stop_lat","stop_lon",
                                                     "zone_id","stop_url","location_type","parent_station","wheelchair_boarding"], extrasaction = 'ignore')
        writer.writeheader()
        
        stops = db.stops.find()
        for stop in stops:
            print("STOP:" + str(strip_non_asciii["stop_id"]))
            writer.writerow({"stop_id":strip_non_asciii(stop["stop_id"]),"stop_code":strip_non_asciii(stop["properties"]["stop_code"]),"stop_name":strip_non_asciii(stop["properties"]["stop_name"]),
                             "stop_desc":strip_non_asciii(stop["properties"]["stop_desc"]),"stop_lat":strip_non_asciii(stop["geometry"]["coordinates"][1]),"stop_lon":strip_non_asciii(stop["geometry"]["coordinates"][0]),
                             "zone_id":strip_non_asciii(stop["properties"]["zone_id"]),"stop_url":strip_non_asciii(stop["properties"]["stop_url"]),"location_type":strip_non_asciii(stop["properties"]["location_type"]),
                             "parent_station":strip_non_asciii(stop["properties"]["location_type"]),"wheelchair_boarding":strip_non_asciii(stop["properties"]["wheelchair_boarding"])})
        outfile.close()
        
def build_stop_times(db,to_directory, filename):
    filepath = os.path.join(to_directory,filename)
    print(filepath)
    with open(filepath, 'wb') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["trip_id","stop_sequence","stop_id","arrival_time","departure_time",
                                                     "stop_headsign","pickup_type","drop_off_type","shape_dist_traveled"], extrasaction = 'ignore')
        writer.writeheader()
        
        trips = db.trips.find()
        for trip in trips:
            for stop_time in trip["stop_times"]:
                print("STOP TIME:" + str(stop_time["seq"]))
                writer.writerow({"trip_id":trip["trip_id"],"stop_sequence": stop_time["seq"],"stop_id": stop_time["stop_id"],
                                 "arrival_time":stop_time["arrival_time"],"departure_time":stop_time["arrival_time"],
                                 "stop_headsign":stop_time["stop_headsign"],"pickup_type":stop_time["pickup_type"],
                                 "drop_off_type":stop_time["drop_off_type"],"shape_dist_traveled":stop_time["shape_dist_traveled"]})
        outfile.close()

def build_trips(db,to_directory, filename):
    filepath = os.path.join(to_directory,filename)
    print(filepath)
    with open(filepath, 'wb') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["route_id","service_id","trip_short_name",
                                                     "trip_headsign","direction_id","block_id","shape_id","trip_id"], extrasaction = 'ignore')
        writer.writeheader()

        trips = db.trips.find()
        for trip in trips:
            print("TRIP:" + str(trip["properties"]["route_id"]))
            services = db.calendar.find({"_id":trip["properties"]["service_id"]})
            for service in services:
                service_id = service["service_id"]
            writer.writerow({"route_id":trip["properties"]["route_id"],"service_id":service_id,"trip_short_name":trip["properties"]["trip_short_name"],
                             "trip_headsign":trip["properties"]["trip_headsign"],"direction_id":trip["properties"]["trip_direction_id"],
                             "block_id":trip["properties"]["trip_block_id"],"shape_id":trip["properties"]["shape_id"],"trip_id":trip["trip_id"]})

        outfile.close()

def builders(to_directory):
        build_agency(db,to_directory, "agency.txt")
        build_calendar(db,to_directory, "calendar.txt")
        build_feed_info(db,to_directory, "feed_info.txt")
        build_frequencies(db,to_directory, "frequencies.txt")
        build_routes(db,to_directory, "routes.txt")
        build_shapes(db,to_directory, "shapes.txt")
        build_stop_times(db,to_directory, "stop_times.txt")
        build_stops(db,to_directory, "stops.txt")
        build_trips(db,to_directory, "trips.txt")
        
'''
Build GTFS files from Database
Params:
to_directory - path directory to build gtfs txt files
'''
def build_gtfs(db,to_directory):
    if not os.path.exists(to_directory):
        os.makedirs(to_directory)
        builders(to_directory)
        
    else:
        for every_file in os.listdir(to_directory):
            filepath = os.path.join(to_directory,every_file)
            try:
                os.path.isfile(filepath)
                os.unlink(filepath)
                print("Old file removed")
                
            except Exception as e:
                print(e)
                
        print("Rebuilding")
        builders(to_directory)
            
#db,client = db_connect('mongouser', 'password', 'localhost','27017', 'plexus')
db,client =  db_connect()

print("Connected to: %s") % (db.get_collection)

#initialize_default_fields(db)

#insert_to_db(db,"stops")
#insert_to_db(db,"calendar")
#insert_to_db(db,"trips")
#insert_to_db(db,"frequencies")
#insert_to_db(db,"stop_times")

build_gtfs(db,"gtfs-plexus-new")
