import TracabModules.scheduleFunctions as sf

"""
Schedule-Script for all competitions with opta as info provider
"""
comp_id = input('Which competition do you want to update? \n'
                '5 - Champions League \n'
                '6 - Europa League \n'
                '9 - Eredivisie \n'
                )

season_id = input('Which season do you want to update? \n')

sf.get_schedule_xml(comp_id, vendor='opta', season_id=season_id)

schedule_filename = 'srml-' + str(comp_id) + '-' + str(season_id) + '-results.xml'
squads_filename = 'srml-' + str(comp_id) + '-' + str(season_id) + '-squads.xml'

# Parse the schedule from xml-file to a pandas.Dataframe
schedule = sf.get_opta_schedule(comp_id, schedule_filename, squads_filename)

# Push schedule to Google Sheets
sf.push_to_google(schedule, league= schedule['League'].iloc[0])
