# README #

Scripts for generating the required files for the NASA Unmanned Aircraft System (UAS) Traffic Management (UTM) Technical Capability Level 3 (TCL3) project. Partially developed GUI.

See: https://utm.arc.nasa.gov/index.shtml for project details.

### What is this repository for? ###

* Generate required data files for NASA UTM TCL3
* v0.1

### How do I get set up? ###

* Dependencies:
	- Python 3
	- PyQt5 (for GUI)

### Basic Usage ###
These programs are written for internal ACUASI use and are not currently configured to be easily run by an outside party.

Parsers and Jupyter Notebooks are found in the `tcl3parsers` directory. All the parsers: `con1.py`, `con2.py`, `saa2.py`, etc. are written as modules so can be imported by other Python programs. The Jupyter Notebook processing files, e.g. `CNS1 Processing.ipynb` are written to use the parser modules and perform the actual processing on the gathered mission data. If you are not using my folder hierarchy they will be less useful.

Parsers require various log files to be passed to them as well as an output file name.

Example usage:
Use `cns1.py` and `flight_data.py` to generate `CNS1.json` and `FLIGHT_DATA.json` files for arducopter flights.

Files:
* 2018-05-18 10-31.log  								(Arducopter dataflash file converted from binary)
* 2018-05-18 10-31_mission_insight.csv  				(Mission Insight information file)
* 2018-05-18 10-31_field_variables.csv  				(Field variable file, captured manually Operators)

* CNS1.json												(Output file name)
* FLIGHT_DATA.json 										(Output file name)

Short Python program to process files:
```
import cns1, flight_data

mi_file_name = "2018-04-27 11-16-16_mission_insight.csv"
dataflash_file_name = "2018-04-27 11-16-16.log"
field_vars_file_name = "2018-04-27 11-16-16_field_variables.csv"

cns1.generate(mi_file_name, dataflash_file_name, field_vars_file_name, "CNS1.json")
flight_data.generate(mi_file_name, dataflash_file_name, "FLIGHT_DATA.json")
```
### Who do I talk to? ###

* Samuel Vanderwaal, samuel.vanderwaal@gmail.com
