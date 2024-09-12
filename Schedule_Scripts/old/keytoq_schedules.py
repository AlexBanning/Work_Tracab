import TracabModules.Internal.scheduleFunctions as sf

"""
Schedule-Script for all competitions with keytoq as info provider
"""

season_id = input('Which season do you want to update? \n')

season_dir = f'Season{str(season_id)[-2:]}-{str(int(season_id) + 1)[-2:]}'

comp_id = int(51)

sf.get_schedule_xml(comp_id, vendor='keytoq', season_dir=season_dir)

filename = 'main.xml'

# Parse the schedule from xml-file to a pandas.Dataframe
schedule = sf.get_keytoq_schedule(filename, season_dir=season_dir)

# Push schedule to Google Sheets
sf.push_to_google(schedule, league=schedule['League'].iloc[0], season_dir=season_dir)
