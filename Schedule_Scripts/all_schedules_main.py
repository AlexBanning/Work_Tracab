from TracabModules.Internal.schedule import Schedule
import json

with open(r'\\10.49.0.250\tracab_neu\07_QC\Scripts\Schedule_script\Season24-25\configs\all_schedules.json', 'r') as file:
    config = json.load(file)


schedule = Schedule(comp_id=config['bl1']['comp_id'], vendor=config['bl1']['vendor'],
                    season_dir=config['bl1']['info_dir'], season_id='2024', spreadsheet_id=config['spreadsheet_id'],
                    server=config['server'], user=config['user'], password=config['password'])
schedule.parse()
