# =====================================================
#   create_event.py
# --------------
#   Create the Element Tree XML object
#   - Based on struct4event.pro
# =====================================================

from .voevent import VOevent

# Generate VOevent obj
def create_event(df, event_type_abrv):
  # Get event list dynamically from dataframe
  # - Obtain all abbrevations between Dimensions and Source column
  header = df.columns
  header_top = header.get_level_values(0)
  dimensions_index = list(header_top).index('Dimensions')
  source_index = list(header_top).index('Source')
  event_types_abrv = header_top[dimensions_index+1:source_index]
  event_type_names = df.iloc[0, dimensions_index+1:source_index].values
  event_types= dict(zip(event_types_abrv, event_type_names))
  df = df.iloc[1:]  # Remove the top line (Full_Name line)
  # print(f'Event type List: {event_types}')

  # Make full event_type string
  event_type={}
  event_type['abrv'], event_type['full'] = event_type_abrv, event_types[event_type_abrv]
  print(event_type['full'])

  # Given the event type, get the list of required and optional parameters'
  required_attr, optional_attr = [], []
  for index, row in df.iterrows():
    parameter, dimensions, attribute_type, source, vo_param_type, r_o, vo_translation, description =  \
      row['Parameter'], row['Dimensions'], row['Type'], row['Source'], row['VOParamType'], row['R/O'], row['VOTranslation'], row['Description']
    required = row.iloc[3+list(event_types.keys()).index(event_type_abrv)]
    # print(f'{input_event_type}, {parameter}, {attribute_type}, {required}, {source}, {vo_param_type}, {r_o}')
    
    # Check if the attribute is required or optional for the specified event type
    match int(required):
      case 9: 
        required_attr.append(parameter)
      case 5: 
        optional_attr.append(parameter)

  # Generate the structure with the required / optional parameters
  voevent_obj = VOevent(event_type, required_attr, optional_attr)

  # Finished - Return the structure
  return voevent_obj





  # # Check if the attribute is required or optional for the specified event type
  # if input_event_type in event_types and required != 0: 
  #   for sub_elem in root:
  #     if sub_elem.tag == vo_param_type.capitalize() \
  #     or (vo_param_type == 'wherewhen' and sub_elem.tag == 'WhereWhen'):
  #       if r_o == 'r':        
  #         match source:
  #           case 'data': ET.SubElement(sub_elem.find('lmsal:data'), parameter)
  #           case 'method': ET.SubElement(sub_elem.find('lmsal:method'), parameter)
  #           case _: ET.SubElement(sub_elem, parameter)
  #       else: 
  #         group_elem = sub_elem.find('Group')
  #         set_optional_param(group_elem, parameter, '')
  #       # elem.text = ''  # Placeholder, replace with actual attribute value
 
  
  # # Dynamically generate different VOParamType groups and associated branches
  # root = ET.Element("voe:VOEvent")
  # for vo_type in vo_type_list:
  #   if vo_type == 'wherewhen': 
  #     sub_elem = ET.SubElement(root, 'WhereWhen')
  #   else: 
  #     sub_elem = ET.SubElement(root, vo_type.capitalize())
  #   ET.SubElement(sub_elem, "lmsal:data")
  #   ET.SubElement(sub_elem, "lmsal:method")
  #   group_elem = ET.SubElement(sub_elem, "Group")
  #   group_elem.set('Name', 'Other_optional')

  # # Iterate through entire dataframe
  # # - Find attributes for the specified event type
  # for index, row in df.iterrows():
  #   parameter, attribute_type, source, vo_param_type, r_o =  \
  #     row['Parameter'], row['Type'], row['Source'], row['VOParamType'], row['R/O']
  #   required = row.iloc[3+list(event_types.keys()).index(input_event_type)]
  #   print(f'{input_event_type}, {parameter}, {attribute_type}, {required}, {source}, {vo_param_type}, {r_o}')
    
  #   # Check if the attribute is required or optional for the specified event type
  #   if input_event_type in event_types and required != 0: 
  #     for sub_elem in root:
  #       if sub_elem.tag == vo_param_type.capitalize() \
  #       or (vo_param_type == 'wherewhen' and sub_elem.tag == 'WhereWhen'):
  #         if r_o == 'r':        
  #           match source:
  #             case 'data': ET.SubElement(sub_elem.find('lmsal:data'), parameter)
  #             case 'method': ET.SubElement(sub_elem.find('lmsal:method'), parameter)
  #             case _: ET.SubElement(sub_elem, parameter)
  #         else: 
  #           group_elem = sub_elem.find('Group')
  #           set_optional_param(group_elem, parameter, '')
  #         # elem.text = ''  # Placeholder, replace with actual attribute value
  
  # # Finished - Return tree structure
  # return root