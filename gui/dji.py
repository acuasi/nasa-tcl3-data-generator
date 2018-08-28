import os
import json
from dji import Dji

d = Dji()

mi_file_path = "/home/samuel/SpiderOak Hive/ACUASI/Code_Repos/nasa-tcl3-data-generator/Example_Files/mission_insight_sample.csv"
dji_file_path = "/home/samuel/SpiderOak Hive/ACUASI/Code_Repos/nasa-tcl3-data-generator/Example_Files/dji/inspire-log.csv"
waypoints_file_path = ""
gcs_loc = json.load(open("/home/samuel/SpiderOak Hive/ACUASI/Code_Repos/"
                         "nasa-tcl3-data-generator/gcs-locations.json"))
gcs_loc1 = gcs_loc["location1"]

state_file = "/home/samuel/SpiderOak Hive/ACUASI/Code_Repos/" \
    "nasa-tcl3-data-generator/UTM-ACUASI-20180208-1405-UASState.csv"
auxiliary_file = "/home/samuel/SpiderOak Hive/ACUASI/Code_Repos/" \
    "nasa-tcl3-data-generator/UTM-ACUASI-20180208-1405-AuxiliaryUASOperation.csv"
aircraft_flight_plan_file = "/home/samuel/SpiderOak Hive/ACUASI/Code_Repos/" \
    "nasa-tcl3-data-generator/UTM-ACUASI-20180208-1405-AircraftFlightPlan.csv"


def test_state():
    """Test creation of UASState file."""
    d.state(mi_file_path, dji_file_path)
    assert(os.path.exists(state_file))
    os.remove(state_file)


def test_auxiliary():
    """Test creation of UASAuxiliary file."""
    d.auxiliary(mi_file_path, dji_file_path, gcs_loc1)
    assert(os.path.exists(auxiliary_file))
    os.remove(auxiliary_file)


def test_flight_plan():
    """Test creation of UASFlightPlan file."""
    d.flight(mi_file_path, waypoints_file_path, dji_file_path)
    assert(os.path.exists(aircraft_flight_plan_file))
    os.remove(aircraft_flight_plan_file)
