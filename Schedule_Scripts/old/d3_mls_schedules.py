import TracabModules.Internal.scheduleFunctions as sf
from pathlib import Path
"""
Schedule-Script for all competitions of the MLS and deltatre as info provider
"""

# Ask the user for the compId and seasonId of the competition which schedule shall be updated
comp_id = input('Which competition do you want to update? \n'
                '1 - MLS \n'
                '2 - PlayOffs \n'
                '6 - MLS League Cup \n'
                '7 - Campeones Cup \n'
                '102 - U.S. OpenCup \n'
                )

season_id = input('Which season do you want to update? \n'
                  '8 - 2024 \n'
                  '9 - 2025 \n'
                  )

season_dir = f'Season{str(int(season_id) + 2016)[-2:]}-{str(int(season_id) + 2017)[-2:]}'

if not Path(fr'N:\07_QC\Scripts\Schedule_script\{season_dir}\MatchInfo').is_dir():
    season_dir = f'Season{str(int(season_id) + 2015)[-2:]}-{str(int(season_id) + 2016)[-2:]}'


# Download the xml-file based on comp and season id
sf.get_schedule_xml(comp_id, vendor='d3_mls', season_dir=season_dir, season_id=season_id)

# Define filename so the schedule function can open it
if comp_id == str(102):
    filename = f'Feed_01_06_basedata_fixtures_MLS-SEA-0001K{season_id}_MLS-COM-00002U.xml'
else:
    filename = f'Feed_01_06_basedata_fixtures_MLS-SEA-0001K{season_id}_MLS-COM-00000' + str(comp_id) + '.xml'

# Parse the schedule from xml-file to a pandas.Dataframe
schedule = sf.get_d3_mls_schedule(int(comp_id), filename, season_dir)

# Push schedule to Google Sheets
sf.push_to_google(schedule, league= schedule['League'].iloc[0], season_dir=season_dir)
