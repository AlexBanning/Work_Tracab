import TracabModules.Internal.scheduleFunctions as sf

"""
Schedule-Script for all competitions with keytoq as info provider
"""

# print('Which season do you want to update?')

# season_id = input()
comp_id = int(51)

sf.get_schedule_xml(comp_id, vendor='keytoq')

filename = 'main.xml'

# Parse the schedule from xml-file to a pandas.Dataframe
schedule = sf.get_keytoq_schedule(filename)

# Push schedule to Google Sheets
sf.push_to_google(schedule, league= schedule[5].iloc[0])
