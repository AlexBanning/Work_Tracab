import TracabModules.Internal.scheduleFunctions as sf

"""
Schedule-Script for all competitions of the MLS and deltatre as info provider
"""

# Ask the user for the compId and seasonId of the competition which schedule shall be updated
comp_id = input('Which competition do you want to update? \n'
                '1 - MLS \n'
                '2 - PlayOffs \n'
                '6 - MLS League Cup \n'
                '7 - Campeones Cup \n'
                )

season_id = input('Which season do you want to update? \n')

# Download the xml-file based on comp and season id
sf.get_schedule_xml(comp_id, vendor='d3_mls', season_id=season_id)

# Define filename so the schedule function can open it
filename = 'Feed_01_06_basedata_fixtures_MLS-SEA-0001K8_MLS-COM-00000' + str(comp_id) + '.xml'

# Parse the schedule from xml-file to a pandas.Dataframe
schedule = sf.get_d3_mls_schedule(int(comp_id), filename)

# Push schedule to Google Sheets
sf.push_to_google(schedule, league= schedule['League'].iloc[0])
