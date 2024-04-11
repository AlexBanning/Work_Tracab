import TracabModules.Internal.scheduleFunctions as sf

"""
Schedule-Script for all competitions with fifa as info provider
"""


comp_id = input('Which competition do you want to update? \n'
                '285026 - FIFA Women WC 2023 \n'
                )

# print('Which season do you want to update?')
#
# if len(comp_id) < 4 or type(comp_id) != int:
#     print('Please insert a valid season!')
#     comp_id = input()
# else:
#     pass


sf.get_schedule_xml(comp_id, vendor='FIFA')

filename = str(comp_id) + '_schedule.xml'

# Parse the schedule from xml-file to a pandas.Dataframe
schedule = sf.get_fifa_schedule(comp_id, filename)

# Push schedule to Google Sheets
sf.push_to_google(schedule, league=schedule['League'].iloc[0])
