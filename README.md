# plexus-route-builder
Builds GTFS files and GeoJSON file of Metro Manila, Philippines from the mongoDB database of Plexus found in thesis-plexus.herokuapp.com

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

<b>Versions</b>
 - Version 1.0.0 08/14/17
   - Manual cleaning. Unclean Version
 - Version 2.0.0 09/21/17
   - Cleaned version. On road 
