"""
The purpose of this code will be to create an overview of the most important statistics of the leagues provided
by Tracab. E.g., some overview/poster that visualizes the team's avg distances, top 10 speeds of a league, etc.
Leagues: MLS, BL1, BL2, Eredivisie, Esktraklasa

- Gateway should theoretically contain all matches of these leagues => All KPIs can be fetched from there
- The overview should present avg values across the whole season and top values. Hence, we need a DB that contains all
  values for all teams and players of the season

KPIs: 1. Avg distances of all teams in league
      2. Top 10 speeds of the season across all players

FETCHING GAMES FROM GW TAKES VERY LONG FOR CERTAIN MATCHES (above 20 retries until code 200) AND SOME MATCHES NOT
FULLY AVAILABLE. ONLY LIVE DATA FOR ALL MATCHES.
"""
from TracabModules.DataManipulation.data_manipulation import GatewayKPIs
from TracabModules.Internal.gateway import GatewayDownloader
from TracabModules.Internal.scheduleFunctions import get_d3_schedule, get_schedule_xml
import time
import logging

"""
Definition of game parameters
"""
EXTR_VERS = '4'
DATA_QUALITY = '0'
game_id = '184558'
vendor_id = '4'

"""
Iterate over all BL matches and retrieve KPIs ------------ NOT FEASIBLE CURRENTLY!!!!!!!!!!!
"""
# GameID and VendorID should be taken out of the schedules of each league
bl1_schedule = get_d3_schedule('51', 'schedule.xml', chdr=False)

game_ids = [bl1_schedule['MatchID']][0].tolist()[0:10]



season_kpis = {}
# Download data
logging.basicConfig(level=logging.INFO)
for game_id in game_ids:
    downloader = GatewayDownloader(game_id, vendor_id, DATA_QUALITY, EXTR_VERS)
    tf08_data, tf08_success = downloader.download_tf08_feed()
    kpis = ['Distance', 'Possession', 'TopSpeedPlayer']
    calculator = GatewayKPIs(tf08_data=tf08_data, kpi_list_tf08=kpis)
    tf08_kpis = calculator.get_tf08_kpis()
    season_kpis.update({game_id: tf08_kpis})
    time.sleep(2)
    logging.info(f'KPIs for match {game_id} have been added.')




