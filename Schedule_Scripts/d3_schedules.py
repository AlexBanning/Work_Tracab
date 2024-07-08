import TracabModules.Internal.scheduleFunctions as sf

"""
Schedule-Script for all competitions with deltatre as data provider
"""

comp_id = input('Which competition do you want to update? \n'
                '15 - 1.Bundesliga - Relegation \n'
                '16 - 2.Bundesliga - Relegation \n'
                '51 - 1.Bundesliga \n'
                '52 - 2.Bundesliga \n'
                '60 - DFB Pokal \n'
                '61 - DFL Supercup \n')

season_id = input('Which season do you want to update? \n')

season_dir = f'Season{str(season_id)[-2:]}-{str(int(season_id) + 1)[-2:]}'

sf.get_schedule_xml(comp_id, vendor='deltatre', season_id=season_id, season_dir=season_dir)

filename = 'schedule.xml'

# Parse the schedule from xml-file to a pandas.Dataframe
schedule = sf.get_d3_schedule(comp_id, filename, season_dir=season_dir)

# Push schedule to Google Sheets
sf.push_to_google(schedule, league=schedule['League'].iloc[0], season_dir=season_dir)
