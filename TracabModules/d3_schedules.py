import TracabModules.scheduleFunctions as sf

"""
Schedule-Script for all competitions with deltatre as data provider
"""

print('Which competition do you want to update? \n'
      '15 - 1.Bundesliga - Relegation \n'
      '16 - 2.Bundesliga - Relegation \n'
      '51 - 1.Bundesliga \n'
      '52 - 2.Bundesliga \n'
      '60 - DFB Pokal \n'
      '61 - DFL Supercup \n')

comp_id = input()

print('Which season do you want to update?')

season_id = input()
# Workaround due to raised (unknown) error when downloading files from ftp
try:
    sf.get_schedule_xml(comp_id, season_id, vendor='deltatre')
except:
    pass

filename = 'schedule.xml'

# Parse the schedule from xml-file to a pandas.Dataframe
schedule = sf.get_d3_schedule(filename)

# Push schedule to Google Sheets
sf.push_to_google(schedule, league= schedule['League'].iloc[0] + '_Test')

