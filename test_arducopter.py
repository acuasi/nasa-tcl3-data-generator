import os
import arducopter
import json

mission_insight_file_path = "/home/samuel/SpiderOak Hive/ACUASI/Code_Repos/nasa-tcl3-data-generator/Example_Files/mission_insight_sample.csv"
tlog_csv_file_path = "/home/samuel/SpiderOak Hive/ACUASI/Code_Repos/nasa-tcl3-data-generator/Example_Files/2018-02-08 14-05-34.csv"
waypoints_file_path = "/home/samuel/SpiderOak Hive/ACUASI/Code_Repos/nasa-tcl3-data-generator/Example_Files/Balloon Launch RTK - S1000.waypoints"
gcs_locations = json.load(open('/home/samuel/SpiderOak Hive/ACUASI/Code_Repos/nasa-tcl3-data-generator/gcs-locations.json')) 
gcs_location1 = gcs_locations["location1"]

state_file = "/home/samuel/SpiderOak Hive/ACUASI/Code_Repos/nasa-tcl3-data-generator/UTM-ACUASI-20180208-1405-UASState.csv"
auxiliary_file = "/home/samuel/SpiderOak Hive/ACUASI/Code_Repos/nasa-tcl3-data-generator/UTM-ACUASI-20180208-1405-AuxiliaryUASOperation.csv"
aircraft_flight_plan_file = "/home/samuel/SpiderOak Hive/ACUASI/Code_Repos/nasa-tcl3-data-generator/UTM-ACUASI-20180208-1405-AircraftFlightPlan.csv"

ardu = arducopter.Arducopter()

def test_state():
	ardu.state(mission_insight_file_path, tlog_csv_file_path)
	assert(os.path.exists(state_file))

def test_auxiliary():
	ardu.auxiliary(mission_insight_file_path, tlog_csv_file_path, gcs_location1)
	assert(os.path.exists(auxiliary_file))

def test_flight_plan():
	ardu.flight(mission_insight_file_path, waypoints_file_path, tlog_csv_file_path)
	assert(os.path.exists(aircraft_flight_plan_file))