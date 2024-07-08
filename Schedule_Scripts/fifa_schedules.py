import TracabModules.Internal.scheduleFunctions as sf

"""
Schedule-Script for all competitions with fifa as info provider
"""


comp_id = input('Which competition do you want to update? \n'
                '285026 - FIFA Women WC 2023 \n'
                )

season_id = input('Which season do you want to update? \n')

season_dir = f'Season{str(season_id)[-2:]}-{str(int(season_id) + 1)[-2:]}'


sf.get_schedule_xml(comp_id, vendor='FIFA', season_dir=season_dir)

filename = str(comp_id) + '_schedule.xml'

# Parse the schedule from xml-file to a pandas.Dataframe
schedule = sf.get_fifa_schedule(comp_id, filename, season_dir=season_dir)

# Push schedule to Google Sheets
sf.push_to_google(schedule, league=schedule['League'].iloc[0], season_dir=season_dir)
