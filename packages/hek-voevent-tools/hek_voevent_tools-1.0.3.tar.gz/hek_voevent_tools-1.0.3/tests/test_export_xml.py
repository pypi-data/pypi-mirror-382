# =====================================================
#   test_config.py
# --------------
#   Unit test for checking XML output
# =====================================================

import unittest
import tempfile
import os
from datetime import datetime
import xml.etree.ElementTree as etree
from hek_voevent_tools import load_config, parse_features_file, create_event, export_event

class TestExportXML(unittest.TestCase):
  def test_export_xml(self):
    # Make the output .xml a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as temp_file:
      temp_path = temp_file.name

    # Make object
    config = load_config()
    csv_data = parse_features_file(config['DEFAULT'].get('specs_location'))
    voevent = create_event(csv_data, 'FL')

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
    export_event(csv_data, voevent, temp_path)

    # Check that file exists
    self.assertTrue(os.path.exists(temp_path))

    # Check xml contents
    tree = etree.parse(temp_path)
    root = tree.getroot()
    what = root.find('.//What') 
    fl_peakflux = what.find('.//Param[@name="FL_PEAKFLUX"]').attrib['value'] 
    how = root.find('.//How') 
    frm_name = how.find('.//{http://www.lmsal.com/helio-informatics/lmsal-v1.0.xsd}FRM_Name').text 
    self.assertEqual(fl_peakflux, "674.229")
    self.assertEqual(frm_name, "Flare Detective - Trigger Module")

    # Remove the temporary xml
    os.remove(temp_path)