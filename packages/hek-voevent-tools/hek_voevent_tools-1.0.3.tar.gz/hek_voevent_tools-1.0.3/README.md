# HEK-VOEvent-Tools
Python module that generates VOEvent XML from user-supplied data.

## Requirements
* Python 3.0.0+
* Pandas 2.3.0+
* Numpy 2.3.0+

## Installation and Setup

(Recommended): Set up a python virtual environment
```
python -m venv .venv
source .venv/bin/activate
```
Run the following commands to install the related dependencies, and then the package itself.
```
pip install pandas
pip install numpy
pip install hek-voevent-tools
```
If you downloaded the package from source, you can install the package locally with the following command
```
pip install -e .
```
Modify the config.ini file to configure the XML output directory at *lib/(Python version)/site-packages/hek_voevent_tools/*. You can also change the voevent spec file location, which by default is https://www.lmsal.com/hek/software/herconfig/VOEvent_Spec.txt

## Supported Event Types and Attributes

The full list of event types and coresponding attributes can be found here: https://www.lmsal.com/hek/VOEvent_Spec.html

Current HEK entries does NOT support the latest VOEvent 2.0 schema.

## How to use

First, import VOEvent-tools
```
from hek_voevent_tools import parse_features_file, create_event, export_event, load_config
```
Load from config.ini
```
config = load_config()
VOEVENT_SPEC = config['DEFAULT'].get('specs_location')
OUTPUT_PATH = config['DEFAULT'].get('output_path')
```
Convert the VOEvent_Spec file into a Pandas dataframe
```
csv_dataframe = parse_features_file(VOEVENT_SPEC)
```
Create the VOEvent object, in which you also provide the event type as a two letter abbreviation as listed in the specs file.
```
voevent = create_event(csv_dataframe, EVENT_TYPE='FL')
```
Assigned required and optional parameters
```
voevent.required['OBS_Observatory'] = 'SDO'
voevent.required['OBS_Instrument'] = 'AIA'
...
voevent.optional['FL_PeakFlux'] = "674.229"
```
Add citations
```
voevent.citation = {
  'action': 'supersedes',
  'description': 'Closing of open event'
}
```
Add a reference
```
voevent.reference.append({
  'name': 'Publication',
  'link': 'http://www.harvard.edu/',
  'type': 'html'
})
```
Display all information from a VOEvent object, including what is required or optional.
```
voevent.help()
```
Export the VOEvent object as an XML file. By default, the file location is defined at output_path in config.ini.
```
export_event(csv_dataframe, voevent, OUTPUT_PATH+'example.xml')
```
Please refer to **demo_FL.py** example below for a full script on using voevent-tools-pkg.

## Running the unit tests from source

(Recommended): Install and run pytests
```
pip install pytest
pytest -v
```
You can also run the unit tests with Python's built-in **unittest**.
```
python -m unittest discover -s tests
```

## Example code
```
# =====================================================
#   demo_FL.py
# --------------
#   Create example for FL
# =====================================================

import os
from datetime import datetime
from hek_voevent_tools import parse_features_file, create_event, export_event, load_config

# Pull from configuration file
config = load_config()
VOEVENT_SPEC = config['DEFAULT'].get('specs_location')
OUTPUT_PATH = config['DEFAULT'].get('output_path')

# User defined inputs
EVENT_TYPE = 'FL'
OUTPUT_FILENAME = 'FL_test.xml'

# Import the VOEvent Schema from .csv to object
print(f'Reading in .csv from [{VOEVENT_SPEC}]...')
csv_data = parse_features_file(VOEVENT_SPEC)

# Add attributes to the event and make it match below
print(f'Creating XML data structure for event type [{EVENT_TYPE}]...')
voevent = create_event(csv_data, EVENT_TYPE)
voevent.required['KB_ArchivURL'] = 'ivo://helio-informatics.org/FL_FlareDetective-TriggerModule_20250703_143416_2025-07-03T08:50:05.835_1' + "_test1"
voevent.required['KB_ArchivID'] = 'ivo://helio-informatics.org/FL_FlareDetective-TriggerModule_20250703_143416_2025-07-03T08:50:05.835_1' + "_test1"
voevent.required['KB_Archivist'] = 'Paolo C. Grigis - pgrigis@cfa.harvard.edu'
voevent.required['KB_ArchivDate'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

voevent.required['OBS_Observatory'] = 'SDO'
voevent.required['OBS_Instrument'] = 'AIA'
voevent.required['OBS_ChannelID'] = '193'
voevent.required['OBS_MeanWavel'] = '193.000'
voevent.required['OBS_WavelUnit'] = 'angstrom'

voevent.required['FRM_Name'] = 'Flare Detective - Trigger Module'
voevent.required['FRM_Identifier'] = 'Feature Finding Team'
voevent.required['FRM_Institute'] = 'SAO'
voevent.required['FRM_HumanFlag'] = 'F'
voevent.required['FRM_ParamSet'] = 'DerivativeThreshold= 3.00000e+00 EndFraction= 2.50000e-01'
voevent.required['FRM_DateRun'] = '2025-07-03T07:34:13.000'
voevent.required['FRM_Contact'] = 'Paolo C. Grigis - pgrigis@cfa.harvard.edu'
voevent.required['FRM_URL'] = 'http://www.cfa.harvard.edu'
voevent.optional['FRM_VersionNumber'] = "0.510000"

voevent.required['Event_StartTime'] = '2025-07-03T08:49:05.835'
voevent.required['Event_PeakTime'] = '2025-07-03T08:50:17.846'
voevent.required['Event_EndTime'] = '2025-07-03T08:51:53.835'
voevent.required['Event_CoordSys'] = 'UTC-HPC-TOPO'
voevent.required['Event_CoordUnit'] = 'arcseconds'
voevent.required['Event_Coord1'] = '-576.000'
voevent.required['Event_Coord2'] = '-345.600'
voevent.required['Event_C1Error'] = '2.00000'
voevent.required['Event_C2Error'] = '2.00000'

voevent.required['BoundBox_C1LL'] = '-440' #Coordinates of lower-left
voevent.required['BoundBox_C2LL'] = '263.2'  #Corner of bounding box
voevent.required['BoundBox_C1UR'] = '-363.2' #Coordinates of upper-right    
voevent.required['BoundBox_C2UR'] = '340'  #Corner of bounding box 

voevent.optional['FL_PeakFlux'] = "674.229"
voevent.optional['FL_PeakFluxUnit'] = "DN/sec/pixel"
voevent.optional['Event_TestFlag'] = 'True'

voevent.citation = {
  'action': 'supersedes',
  'description': 'Closing of open event'
}

voevent.reference.append({
  'name': 'Publication',
  'link': 'http://www.harvard.edu/',
  'type': 'html'
})

# Export the structure to an XML file
voevent.help()
os.makedirs(OUTPUT_PATH, exist_ok=True)
export_event(csv_data, voevent, OUTPUT_PATH+OUTPUT_FILENAME)
```