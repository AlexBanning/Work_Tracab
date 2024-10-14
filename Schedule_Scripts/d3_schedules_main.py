from TracabModules.Internal.schedule import Schedule
import json

with open(r'\\10.49.0.250\tracab_neu\07_QC\Scripts\Schedule_script\configs\d3_creds.json', 'r') as file:
    config = json.load(file)

for comp_id in config['comp_ids']:
    schedule = Schedule(comp_id=comp_id, vendor='deltatre',season_id=config['season_id'],
                        spreadsheet_id=config['spreadsheet_id'], server=config['server'],
                                   user=config['user'], password=config['password'])
    schedule.parse()