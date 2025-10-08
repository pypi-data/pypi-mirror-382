# =====================================================
#   voevent.py
# --------------
#   Class definition for VOEvent
# =====================================================

class VOevent:
  event_type: str
  event_fullname: str
  description: str

  # First time initialization - generate attributes from given lists
  def __init__(self, event_type, required_list, optional_list):
    self.event_type = event_type['abrv']
    self.event_fullname = event_type['full']
    self.required = {key: "" for key in required_list}
    self.optional = {key: "" for key in optional_list}
    self.description = None
    self.citation = []
    self.reference = []

    self.required['Event_Type'] = f"{event_type['abrv']}: {event_type['full']}"
    self.required['KB_ArchivID'] = 'Reserved for KB archivist: KB entry identifier'
    self.required['KB_Archivist'] = 'Reserved for KB archivist: KB entry made by'
    self.required['KB_ArchivDate'] = 'Reserved for KB archivist: KB entry date'
    self.required['KB_ArchivURL'] = 'Reserved for KB archivist: URL to suppl. info.'
    self.required['Event_StartTime'] = '1492-10-12 00:00:00'
    self.required['Event_EndTime'] = '1492-10-12 00:00:00'
    # self.required['Event_Expires'] = '1492-10-12 00:00:00'

  # Display the supported feature list

  # Display details of attributes
  def help(self):
    print('==============================')
    print('Required Attributes: ')
    print('-------------------- ')
    for key, value in self.required.items(): print(f'{key}: {value}')
    print()

    print('Optional Attributes: ')
    print('-------------------- ')
    for key, value in self.optional.items(): print(f'{key}: {value}')
    print()
    print("For further info, go to http://www.lmsal.com/helio-informatics/hpkb/VOEvent_Spec.html")
    print('==============================')

  # String representation of class 
  def __repr__(self):
    return f'''VOevent [{self.event_type}]
    
---------------
required={self.required}

optional={self.optional}
'''
    # return f"VOevent(type={self.event_type}\nrequired={self.required}\noptional={self.optional})"