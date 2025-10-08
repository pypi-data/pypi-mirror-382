import os
import configparser

def load_config(config_file: str = None):
  config = configparser.ConfigParser()

  # Default is config.ini in same folder
  if config_file is None:  
      config_file = os.path.join(os.path.dirname(__file__), "config.ini")
  if not os.path.exists(config_file):
      raise FileNotFoundError(f"Config file not found: {config_file}")

  config.read(config_file)
  return config