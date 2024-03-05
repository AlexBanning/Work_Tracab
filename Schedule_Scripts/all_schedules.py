import TracabModules.scheduleFunctions as sf

"""
Schedule-Script for all main competitions we are covering in the 23/24 season 
"""

"""
Create MLS Schedule
"""
sf.get_schedule_xml(1, vendor='d3_mls', season_id=2024)


# Define filename so the schedule function can open it
mls_filename = 'Feed_01_06_basedata_fixtures_MLS-SEA-0001K8_MLS-COM-00000' + str(1) + '.xml'


# Parse the schedule from xml-file to a pandas.Dataframe
mls_schedule = sf.get_d3_mls_schedule(comp_id=1,filename=mls_filename)

"""
Create BL1 Schedule
"""
# Download the xml-file based on comp and season id
sf.get_schedule_xml(51, vendor='deltatre', season_id=2023)

# Define filename so the schedule function can open it
bl_filename = 'schedule.xml'

# Parse the schedule from xml-file to a pandas.Dataframe
bl_schedule = sf.get_d3_schedule(comp_id=51, filename=bl_filename)

"""
Create BL2 Schedule
"""

# Download the xml-file based on comp and season id
sf.get_schedule_xml(52, vendor='deltatre', season_id=2023)

# Define filename so the schedule function can open it
blt_filename = 'schedule.xml'

# Parse the schedule from xml-file to a pandas.Dataframe
blt_schedule = sf.get_d3_schedule(comp_id=52, filename=blt_filename)


""" 
Create Eredivisie Schedule
"""
# Download the xml-file based on comp and season id
sf.get_schedule_xml(9, vendor='opta', season_id=2023)

schedule_filename = 'srml-' + str(9) + '-' + str(2023) + '-results.xml'
squads_filename = 'srml-' + str(9) + '-' + str(2023) + '-squads.xml'

# Parse the schedule from xml-file to a pandas.Dataframe
opta_schedule = sf.get_opta_schedule(comp_id=9, schedule_filename=schedule_filename, squad_filename=squads_filename)

"""
Create Ekstraklasa Schedule
"""

comp_id = int(51)

sf.get_schedule_xml(comp_id, vendor='keytoq')

filename = 'main.xml'

# Parse the schedule from xml-file to a pandas.Dataframe
ktq_schedule = sf.get_keytoq_schedule(filename)

"""
Push MLS Schedule
"""
# Push schedule to Google Sheets
sf.push_to_google(mls_schedule, league=mls_schedule['League'].iloc[0])
"""
Push BL1 Schedule
"""
# Push schedule to Google Sheets
sf.push_to_google(bl_schedule, league=bl_schedule['League'].iloc[0])
"""
Push BL2 Schedule
"""
# Push schedule to Google Sheets
sf.push_to_google(blt_schedule, league=blt_schedule['League'].iloc[0])
"""
Push Eredivisie Schedule
"""
# Push schedule to Google Sheets
sf.push_to_google(opta_schedule, league=opta_schedule['League'].iloc[0])
"""
Push Ekstraklasa Schedule
"""
# Push schedule to Google Sheets
sf.push_to_google(ktq_schedule, league=ktq_schedule['League'].iloc[0])
