from TracabModules.Internal.schedule import Schedule
import json

with open(r'\\10.49.0.250\tracab_neu\07_QC\Scripts\Schedule_script\Season24-25\configs\mls_creds.json', 'r') as file:
    config = json.load(file)

for comp_id in config['comp_ids']:
    schedule = Schedule(comp_id=comp_id, vendor='d3_mls',
                        season_dir=config['info_dir'], season_id=config['season_id'],
                        spreadsheet_id=config['spreadsheet_id'], server=config['server'],
                                   user=config['user'], password=config['password'])
    schedule.parse()