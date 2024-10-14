from TracabModules.Internal.schedule import Schedule
import json

with open(r'\\10.49.0.250\tracab_neu\07_QC\Scripts\Schedule_script\configs\all_schedules.json', 'r') as file:
    config = json.load(file)


bl1_schedule = Schedule(comp_id=config['bl1']['comp_id'], vendor=config['bl1']['vendor'],
                    season_id=config['bl1']['season_id'],
                    spreadsheet_id=config['spreadsheet_id'], server=config['server'],
                        user=config['user'], password=config['password'])
bl1_schedule.parse()

bl2_schedule = Schedule(comp_id=config['bl2']['comp_id'], vendor=config['bl2']['vendor'],
                    season_id=config['bl2']['season_id'],
                    spreadsheet_id=config['spreadsheet_id'], server=config['server'],
                        user=config['user'], password=config['password'])
bl2_schedule.parse()

mls_schedule = Schedule(comp_id=config['mls']['comp_id'], vendor=config['mls']['vendor'],
                    season_id=config['mls']['season_id'],
                    spreadsheet_id=config['spreadsheet_id'], server=config['server'],
                        user=config['user'], password=config['password'])
mls_schedule.parse()

eredivisie_schedule = Schedule(comp_id=config['eredivisie']['comp_id'], vendor=config['eredivisie']['vendor'],
                    season_id=config['eredivisie']['season_id'],
                    spreadsheet_id=config['spreadsheet_id'], server=config['server'],
                               user=config['user'], password=config['password'])
eredivisie_schedule.parse()

ekstraklasa_schedule = Schedule(comp_id=config['ekstraklasa']['comp_id'], vendor=config['ekstraklasa']['vendor'],
                    season_id=config['ekstraklasa']['season_id'],
                    spreadsheet_id=config['spreadsheet_id'], server=config['server'],
                                user=config['user'], password=config['password'])
ekstraklasa_schedule.parse()
