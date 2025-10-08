# =====================================================
#   Export_event.py
# --------------
#   Generate an XML based on provided VOevent obj
# =====================================================

import xml.etree.ElementTree as etree
from datetime import datetime

class Error(Exception):
  pass

# Imports
# * DF - Dataframe object from the parsed .csv file
# * 
def export_event(df, voevent, output_file): 
  NSMAP = {
    'voe': "http://www.ivoa.net/xml/VOEvent/v1.1",
    'stc': "http://www.ivoa.net/xml/STC/stc-v1.30.xsd",
    'lmsal': "http://www.lmsal.com/helio-informatics/lmsal-v1.0.xsd",
    'xsi': "http://www.w3.org/2001/XMLSchema-instance"
  }

  root = etree.Element(
    '{http://www.ivoa.net/xml/VOEvent/v1.1}VOEvent',
    nsmap=NSMAP,
    ivorn=voevent.required['KB_ArchivID'],
    role="observation",
    version="1.1",
    attrib={"{http://www.w3.org/2001/XMLSchema-instance}schemaLocation":
            "http://www.ivoa.net/xml/VOEvent/v1.1 http://www.lmsal.com/helio-informatics/VOEvent-v1.1.xsd"}
  )

  # Create XML structure
  # Get event list dynamically from dataframe
  # - Obtain all abbrevations between Dimensions and Source column
  header = df.columns
  header_top = header.get_level_values(0)
  dimensions_index = list(header_top).index('Dimensions')
  source_index = list(header_top).index('Source')
  source_index = list(header_top).index('Type')
  event_types_abrv = header_top[dimensions_index+1:source_index]
  event_type_names = df.iloc[0, dimensions_index+1:source_index].values
  event_types= dict(zip(event_types_abrv, event_type_names))
  df = df.iloc[1:]  # Remove the top line (Full_Name line)
  print(f'Event type List: {event_types}')

  # Get all VOParamType groups list dynamically from dataframe
  # - What do we do with EventMap_URL with no group?
  # - Currently the '-' group is removed
  vo_type_list = df[('VOParamType')].unique()
  vo_type_list = list(filter(lambda x: x != '-', vo_type_list)) 
  print(f'VOParamType list: {vo_type_list}')

  
  # Object Validation
  try:
    # Validate that all parameters in required / optional exist according to .csv
    # ---------------------
    combined_dict = {**voevent.required, **voevent.optional}
    combined_dict_keys = list(combined_dict.keys())
    not_matched = [item for item in combined_dict_keys if item not in df['Parameter'].values]
    if len(not_matched)>0: raise Error(f'Unknown attributes found - {not_matched}')

    # Requirements validation (as export_event.pro has it)
    # ---------------------
    validate, err_list = True, [] 
    for key, value in voevent.required.items():
      if value == "" or None:
        print(f"Required parameter '[{key}]' value is missing!")
        err_list.append(key)
    if validate == False: raise Error(f'Required keys {err_list} have no values!')
    print('All voevent.required values filled')

    # Type check validation (as export_event.pro has it)
    # ---------------------
    validate, err_list = True, []
    for key, value in combined_dict.items():
      value_type = df[df['Parameter'] == key].iloc[0]['Type']
      if key == 'Event_CoordSys':
        if str(value).lower() not in ['utc-hpc-topo', 'utc-hpr-topo', 'utc-hgs-topo', 'utc-hgc-topo', 'utc-hcr-topo']:
          validate = False
          err_list.append(key)
          print(f"Invalid value for '{key}': {value}!")
          print('''---------------------------Error--------------------------
          Please use one of the following coordinate systems
          for the required.coord_sys attribute.
          Cartesian helio-projective:      "utc-hpc-topo"
          Polar helio-projective:          "utc-hpr-topo"
          Stonyhurst heliographic:         "utc-hgs-topo"
          Carrington heliographic:         "utc-hgc-topo"
          Pol. angle and radius (for CMEs):"utc-hcr-topo"
          ----------------------------------------------------------
          For details, go to:
          http://www.ivoa.net/Documents/PR/VOE/VOEvent-20060629.html
          ----------------------------------------------------------''')
        else:
          print(f"Valid value for '{key}': {value} (string / Event_CoordSys)")
      elif value is not "" or None:
        if validate_type(value, value_type):
          print(f"Valid value for '{key}': {value} ({value_type})")
        else:
          validate = False
          err_list.append(key)
          print(f"Invalid value for '{key}': {value} (Expected: {value_type})!")
    if validate == False: raise Error(f'Keys {err_list} have invalid value types!')
  except Error as e:
    print(f'ERROR: {e}')
    exit()
  print('All voevent.required and voevent.optional values types are checked')

  # Required for ALL types... Manually constructed tree (r in R/O column)
  # ---------------------
  # Who
  Who = etree.SubElement(root, "Who")
  Who.append(etree.Comment(" Data pertaining to curation "))
  etree.SubElement(Who, "AuthorIVORN").text = voevent.required['KB_ArchivURL']
  Author = etree.SubElement(Who, "Author")
  etree.SubElement(Author, "contactName").text = voevent.required['KB_Archivist']
  etree.SubElement(Who, "Date").text = voevent.required['KB_ArchivDate']

  # What
  What = etree.SubElement(root, "What")
  What.append(etree.Comment(" Data about what was measured/observed. "))

  # WhereWhen
  WhereWhen = etree.SubElement(root, "WhereWhen")
  WhereWhen.append(etree.Comment(" Data pertaining to when and where something occured "))
  ObsDataLocation = etree.SubElement(WhereWhen, "ObsDataLocation", xmlns="http://www.ivoa.net/xml/STC/stc-v1.30.xsd")

  ObservatoryLocation = etree.SubElement(ObsDataLocation, "ObservatoryLocation")
  etree.SubElement(ObservatoryLocation, "AstroCoordSystem")
  etree.SubElement(ObservatoryLocation, "AstroCoords", id=voevent.required['Event_CoordSys'], coord_system_id=voevent.required['Event_CoordSys'])

  ObservationLocation = etree.SubElement(ObsDataLocation, "ObservationLocation", id=voevent.required['OBS_Observatory'])
  etree.SubElement(ObservationLocation, "AstroCoordSystem")

  AstroCoords_Obs = etree.SubElement(ObservationLocation, "AstroCoords", coord_system_id=voevent.required['Event_CoordSys'])

  Time = etree.SubElement(AstroCoords_Obs, "Time")
  TimeInstant = etree.SubElement(Time, "TimeInstant")
  etree.SubElement(TimeInstant, "ISOTime").text = voevent.required['Event_StartTime']

  Position2D = etree.SubElement(AstroCoords_Obs, "Position2D", unit=voevent.required['Event_CoordUnit'])
  Value2 = etree.SubElement(Position2D, "Value2")
  etree.SubElement(Value2, "C1").text = voevent.required['Event_Coord1']
  etree.SubElement(Value2, "C2").text = voevent.required['Event_Coord2']
  Error2 = etree.SubElement(Position2D, "Error2")
  etree.SubElement(Error2, "C1").text = voevent.required['Event_C1Error']
  etree.SubElement(Error2, "C2").text = voevent.required['Event_C2Error']

  AstroCoordArea = etree.SubElement(ObservationLocation, "AstroCoordArea", coord_system_id=voevent.required['Event_CoordSys'])
  TimeInterval = etree.SubElement(AstroCoordArea, "TimeInterval")
  StartTime = etree.SubElement(TimeInterval, "StartTime")
  etree.SubElement(StartTime, "ISOTime").text = voevent.required['Event_StartTime']
  StopTime = etree.SubElement(TimeInterval, "StopTime")
  etree.SubElement(StopTime, "ISOTime").text = voevent.required['Event_EndTime']
  
  # Need to manually calculate size of box from given parameters
  Box2 = etree.SubElement(AstroCoordArea, "Box2")
  Center = etree.SubElement(Box2, "Center")
  Box2_Size_C1 = float(voevent.required['BoundBox_C1UR']) - float(voevent.required['BoundBox_C1LL'])
  Box2_Size_C2 = float(voevent.required['BoundBox_C2UR']) - float(voevent.required['BoundBox_C2LL'])
  Box2_Center_C1 = (Box2_Size_C1/2)+float(voevent.required['BoundBox_C1LL'])
  Box2_Center_C2 = (Box2_Size_C2/2.)+float(voevent.required['BoundBox_C2LL'])
  etree.SubElement(Center, "C1").text = str("{:.5f}".format(Box2_Center_C1))
  etree.SubElement(Center, "C2").text = str("{:.5f}".format(Box2_Center_C2))
  Size = etree.SubElement(Box2, "Size")
  etree.SubElement(Size, "C1").text = str("{:.5f}".format(Box2_Size_C1))
  etree.SubElement(Size, "C2").text = str("{:.5f}".format(Box2_Size_C2))

  # How
  How = etree.SubElement(root, "How")
  How.append(etree.Comment("  Data pertaining to how the feature/event detection was performed  "))
  lmsal_data = etree.SubElement(How, "{http://www.lmsal.com/helio-informatics/lmsal-v1.0.xsd}data")
  etree.SubElement(lmsal_data, "{http://www.lmsal.com/helio-informatics/lmsal-v1.0.xsd}OBS_ChannelID").text = voevent.required['OBS_ChannelID']
  etree.SubElement(lmsal_data, "{http://www.lmsal.com/helio-informatics/lmsal-v1.0.xsd}OBS_Instrument").text = voevent.required['OBS_Instrument'] 
  etree.SubElement(lmsal_data, "{http://www.lmsal.com/helio-informatics/lmsal-v1.0.xsd}OBS_MeanWavel").text = voevent.required['OBS_MeanWavel']
  etree.SubElement(lmsal_data, "{http://www.lmsal.com/helio-informatics/lmsal-v1.0.xsd}OBS_WavelUnit").text = voevent.required['OBS_WavelUnit']
  lmsal_method = etree.SubElement(How, "{http://www.lmsal.com/helio-informatics/lmsal-v1.0.xsd}method")
  etree.SubElement(lmsal_method, "{http://www.lmsal.com/helio-informatics/lmsal-v1.0.xsd}FRM_Contact").text = voevent.required['FRM_Contact']
  etree.SubElement(lmsal_method, "{http://www.lmsal.com/helio-informatics/lmsal-v1.0.xsd}FRM_DateRun").text = voevent.required['FRM_DateRun']
  etree.SubElement(lmsal_method, "{http://www.lmsal.com/helio-informatics/lmsal-v1.0.xsd}FRM_HumanFlag").text = voevent.required['FRM_HumanFlag']
  etree.SubElement(lmsal_method, "{http://www.lmsal.com/helio-informatics/lmsal-v1.0.xsd}FRM_Identifier").text = voevent.required['FRM_Identifier']
  etree.SubElement(lmsal_method, "{http://www.lmsal.com/helio-informatics/lmsal-v1.0.xsd}FRM_Institute").text = voevent.required['FRM_Institute']
  etree.SubElement(lmsal_method, "{http://www.lmsal.com/helio-informatics/lmsal-v1.0.xsd}FRM_Name").text = voevent.required['FRM_Name']
  etree.SubElement(lmsal_method, "{http://www.lmsal.com/helio-informatics/lmsal-v1.0.xsd}FRM_ParamSet").text = voevent.required['FRM_ParamSet']

  # Why
  Why = etree.SubElement(root, "Why")
  # Extra case for event probability
  if "Event_Probability" in voevent.optional and voevent.optional["Event_Probability"] is not "":
    etree.SubElement(Why, "Param", name="Inference", probability=voevent.optional["Event_Probability"])
  # etree.SubElement(Why, "Inference", probability="Inf")
  etree.SubElement(Why, "Concept").text = voevent.event_fullname
  etree.SubElement(Why, "EVENT_TYPE").text = voevent.required['Event_Type']
  if voevent.description: etree.SubElement(Why, "Description").text = voevent.description 

  # Map string to branches
  BRANCHES = {
    'who': Who,
    'what': What,
    'wherewhen': WhereWhen,
    'why': Why,
    'how': How
  }

  # Required for specified event type (o in R/O column)
  # ---------------------
  # Group = etree.SubElement(WhereWhen, "Group", name="Flare_required")
  # etree.SubElement(Group, "Param", name="EVENT_PEAKTIME", value=f"{voevent.required['Event_PeakTime']}")
  for key, value in voevent.required.items():
    row = df[df['Parameter'] == key].iloc[0]
    if row['R/O'] == 'r': continue
    branch, group_name  = BRANCHES[row['VOParamType']], f"{voevent.event_fullname}_required"
    group = branch.find(f"./Group[@name='{group_name}']")
    if group is None: group = etree.SubElement(branch, "Group", name=group_name)
    etree.SubElement(group, "Param", name=row['Parameter'].upper(), value=value)

  # Fully Optional (o in R/O column)
  # ---------------------
  for key, value in voevent.optional.items():
    if value == "": continue
    row = df[df['Parameter'] == key].iloc[0]
    branch, group_name  = BRANCHES[row['VOParamType']], f"{voevent.event_fullname}_optional"
    group = branch.find(f"./Group[@name='{group_name}']")
    if group is None: group = etree.SubElement(branch, "Group", name=group_name)
    etree.SubElement(group, "Param", name=row['Parameter'].upper(), value=value)

  # Reference
  # ---------------------
  etree.SubElement(root, "Reference", name='FRM_URL', uri=voevent.required['FRM_URL'])
  for ref in voevent.reference:
    etree.SubElement(root, "Reference", name=ref['name'], type=ref['type'], link=ref['link'])

  # Citation
  if voevent.citation:
    if voevent.citation['action'] not in ['action', 'supersedes', 'retraction']:
      print('ERROR: Citation action must be: followup / supersedes / retraction')
      exit()
    Citations = etree.SubElement(root, "Citations")
    etree.SubElement(Citations, "EventIVORN", action=voevent.citation['action']).text = voevent.required['KB_ArchivID']
    etree.SubElement(Citations, "Description").text = voevent.citation['description']

  # Export
  # ---------------------
  # Print as string
  # xml_bytes = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8')
  # print(xml_bytes.decode('utf-8'))

  # Write out to file
  etree.indent(root, space="  ", level=0)
  tree = etree.ElementTree(root)
  tree.write(output_file, encoding="utf-8", xml_declaration=True)
  print(f'Finished! Exported XML to [{output_file}]')
  print()

# Define the function to validate the value type
def validate_type(value, type):
  date_formats = [
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f" # ISO but with milliseconds
  ]
  match type:
    case 'float':  
      try: 
        float(value) 
        return True
      except ValueError: return False
    case 'string': 
      try: 
        str(value) 
        return True
      except ValueError: return False 
    case 'integer' | 'long': # In Python 3, long is equivalent to int
      try: 
        int(value) 
        return True
      except ValueError: return False 
    case 'boolean': return str(value).lower() in ['true', 'false', 't', 'f']
    case 'polygon': return True  
    case 'line': return True
    case 'datetime':
      for fmt in date_formats:
        try:
          datetime.strptime(value, fmt)
          return True
        except ValueError: continue
      return False
    case _: return False