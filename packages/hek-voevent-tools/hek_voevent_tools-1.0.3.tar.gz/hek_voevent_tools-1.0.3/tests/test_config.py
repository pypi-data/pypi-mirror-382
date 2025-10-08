# =====================================================
#   test_config.py
# --------------
#   Unit test for configuration file
# =====================================================

import unittest
from hek_voevent_tools import load_config

class TestConfig(unittest.TestCase):
  def test_load_config(self):
    config = load_config()
    voevent_spec = config['DEFAULT'].get('specs_location')
    output_path = config['DEFAULT'].get('output_path')

    # Check that configurations exists as strings
    self.assertIsInstance(voevent_spec, str)
    self.assertIsInstance(output_path, str)