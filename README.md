# plexus-route-builder
Builds GTFS files and GeoJSON file from the old mongoDB database of Plexus found in thesis-plexus.herokuapp.com

<b>Building from Exsiting MongoDB Database</b>

 - Using <i>gtfs-builder.py</i>, run the following methods to pull the old route database from Plexus MongoDB store.

<b>build_gtfs([db_connection], [directory_folder])</b>
 - calls <b>builders([to_directory])</b>, creating GTFS txt files in directory folder.
 
            -  build_agency(db,to_directory, "agency.txt")
            -  build_calendar(db,to_directory, "calendar.txt")
            -  build_feed_info(db,to_directory, "feed_info.txt")
            -  build_frequencies(db,to_directory, "frequencies.txt")
            -  build_routes(db,to_directory, "routes.txt")
            -  build_shapes(db,to_directory, "shapes.txt")
            -  build_stop_times(db,to_directory, "stop_times.txt")
            -  build_stops(db,to_directory, "stops.txt")
            -  build_trips(db,to_directory, "trips.txt")

<b>initialize_default_field([db_connection])</b>
  - initializes restore from routes.bson if routes table in Mongo Database is empty
  
<b>insert_to_db([db_connection], [modelname])</b>
  - initializes remaining data from GTFS text files to MongoDB database.
  - stops, calendar, trips, frequencies, stop_times (CLEAN)
