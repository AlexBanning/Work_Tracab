import TracabModules.Internal.scheduleFunctions as sf

"""
Schedule-Script for all main competitions we are covering in the 24/25 season 

To Edit:
- season_id Relevant to fetch the most up to date schedule
- season_dir Relevant for Schedule-Script folder on NAS
"""

import json
from pathlib import Path

# Load configuration
config_path = Path(r'C:\Users\alexa\Desktop\all_schedule_creds.json')
with config_path.open() as config_file:
    config = json.load(config_file)

# Accessing values
mls_season = config['mls_season']
season = config['season']
info_dir = config['info_dir']
"""
Create MLS Schedule
"""
sf.get_schedule_xml(1, vendor='d3_mls', season_id=mls_season, season_dir=info_dir)


# Define filename so the schedule function can open it
mls_filename = 'Feed_01_06_basedata_fixtures_MLS-SEA-0001K8_MLS-COM-00000' + str(1) + '.xml'


# Parse the schedule from xml-file to a pandas.Dataframe
mls_schedule = sf.get_d3_mls_schedule(comp_id=1,filename=mls_filename, season_dir=info_dir)

"""
Create BL1 Schedule
"""
# Download the xml-file based on comp and season id
sf.get_schedule_xml(51, vendor='deltatre', season_id=season, season_dir=info_dir)

# Define filename so the schedule function can open it
bl_filename = 'schedule.xml'

# Parse the schedule from xml-file to a pandas.Dataframe
bl_schedule = sf.get_d3_schedule(comp_id=51, filename=bl_filename, season_dir=info_dir)

"""
Create BL2 Schedule
"""

# Download the xml-file based on comp and season id
sf.get_schedule_xml(52, vendor='deltatre', season_id=season, season_dir=info_dir)

# Define filename so the schedule function can open it
blt_filename = 'schedule.xml'

# Parse the schedule from xml-file to a pandas.Dataframe
blt_schedule = sf.get_d3_schedule(comp_id=52, filename=blt_filename, season_dir=info_dir)


""" 
Create Eredivisie Schedule
"""
# Download the xml-file based on comp and season id
sf.get_schedule_xml(9, vendor='opta', season_id=season, season_dir=info_dir)

schedule_filename = f'srml-9-{season}-results.xml'
squads_filename = f'srml-9{season}-squads.xml'

# Parse the schedule from xml-file to a pandas.Dataframe
opta_schedule = sf.get_opta_schedule(comp_id=9, schedule_filename=schedule_filename, squad_filename=squads_filename, season_dir=info_dir)

"""
Create Ekstraklasa Schedule
"""

comp_id = int(51)

sf.get_schedule_xml(comp_id, vendor='keytoq', season_dir=info_dir)

filename = 'main.xml'

# Parse the schedule from xml-file to a pandas.Dataframe
ktq_schedule = sf.get_keytoq_schedule(filename, season_dir=info_dir)

"""
Push MLS Schedule
"""
# Push schedule to Google Sheets
sf.push_df_to_google(mls_schedule, spreadsheet_id='1f7KgwvUb4hzMmavsHP_vRb0nwPgt_wntbZKjgYE4HGw',
                     worksheet=mls_schedule['League'].iloc[0])
"""
Push BL1 Schedule
"""
# Push schedule to Google Sheets
sf.push_df_to_google(bl_schedule, spreadsheet_id='1f7KgwvUb4hzMmavsHP_vRb0nwPgt_wntbZKjgYE4HGw',
                     worksheet=bl_schedule['League'].iloc[0])
"""
Push BL2 Schedule
"""
# Push schedule to Google Sheets
sf.push_df_to_google(blt_schedule, spreadsheet_id='1f7KgwvUb4hzMmavsHP_vRb0nwPgt_wntbZKjgYE4HGw',
                     worksheet=blt_schedule['League'].iloc[0])
"""
Push Eredivisie Schedule
"""
# Push schedule to Google Sheets
sf.push_df_to_google(opta_schedule, spreadsheet_id='1f7KgwvUb4hzMmavsHP_vRb0nwPgt_wntbZKjgYE4HGw',
                     worksheet=opta_schedule['League'].iloc[0])
"""
Push Ekstraklasa Schedule
"""
# Push schedule to Google Sheets
sf.push_df_to_google(ktq_schedule, spreadsheet_id='1f7KgwvUb4hzMmavsHP_vRb0nwPgt_wntbZKjgYE4HGw',
                     worksheet=ktq_schedule['League'].iloc[0])
