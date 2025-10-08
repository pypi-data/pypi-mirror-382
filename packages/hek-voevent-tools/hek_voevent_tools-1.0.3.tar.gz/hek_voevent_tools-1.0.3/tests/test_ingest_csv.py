# =====================================================
#   test_config.py
# --------------
#   Unit test for ingesting the CSV spec file
# =====================================================

import unittest
import pandas as pd
from hek_voevent_tools import load_config, parse_features_file

class TestIngest(unittest.TestCase):
  def test_ingest_csv(self):
    config = load_config()
    voevent_spec = config['DEFAULT'].get('specs_location')
    csv_data = parse_features_file(voevent_spec)

    # Check that the csv is read
    self.assertIsInstance(csv_data, pd.DataFrame)
