# =====================================================
#   ingest_specs.py
# --------------
#   Parse VOEvent Spec page
# =====================================================

import io
import requests
import pandas as pd

class Error(Exception):
  pass

# Import CSV and return data object
def parse_features_file(url):
  try:
    response = requests.get(url)
    if response.status_code == 200:
      txt_io = io.StringIO(response.text)
      features = pd.read_csv(txt_io, skiprows=2, header=[0])    
      return features.dropna(how='all')
    else: 
      raise Error('Failed to fetch file. [Status: {response.status_code}]')
  except Exception as e:
    print(f'Failed to load CSV: {e}')
    exit()

