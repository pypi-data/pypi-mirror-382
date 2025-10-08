# =====================================================
#   test_config.py
# --------------
#   Unit test for creating VOevent 
# =====================================================

import unittest
from hek_voevent_tools import load_config, parse_features_file, create_event

class TestCreateEvent(unittest.TestCase):
  def test_create_event(self):
    config = load_config()
    voevent_spec = config['DEFAULT'].get('specs_location')
    csv_data = parse_features_file(voevent_spec)

    # Check event creation
    voevent = create_event(csv_data, 'FL')
    self.assertEqual(voevent.event_type, 'FL')

    # Check for parameters
    voevent.required['FRM_Name'] = 'Flare Detective - Trigger Module'
    voevent.optional['FL_PeakFlux'] = "674.229"
    self.assertEqual(voevent.required['KB_ArchivURL'], 'Reserved for KB archivist: URL to suppl. info.')
    self.assertEqual(voevent.required['FRM_Name'], 'Flare Detective - Trigger Module')
    self.assertEqual(voevent.optional['FL_PeakFlux'], '674.229')