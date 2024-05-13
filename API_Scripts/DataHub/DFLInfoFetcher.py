"""
club_id_link: f'https://httpget.distribution.production.datahub-sts.de/DeliveryPlatform/REST/PullOnce/STS1-PROD-UCT1-TEST/DFL-01.04-Stammdaten-Vereine/{season_id}_{comp_id}'
player_info_link : f'https://httpget.distribution.production.datahub-sts.de/DeliveryPlatform/REST/PullOnce/datahub-ftp1-plus-2222/DFL-01.05-Stammdaten-Personen_Spieler/{club_id}_{season_id}'

"""

from TracabModules.External.DataHub import DataHub
import requests
from bs4 import BeautifulSoup

datahub_download = DataHub()
season_id = datahub_download.season_id()
comp_id = datahub_download.sts_competition_id(tracab_id='51')
club_id_link = (f'https://httpget.distribution.production.datahub-sts.de/DeliveryPlatform/REST/PullOnce/STS1-PROD-UCT1'
                f'-TEST/DFL-01.04-Stammdaten-Vereine/{season_id}_{comp_id}')
club_id_response = requests.get(club_id_link)
club_id_xml_data = club_id_response.text
club_id_soup = BeautifulSoup(club_id_xml_data, 'xml')
clubs = {x['LongName']: x['ClubId'] for x in club_id_soup.find_all('Club')}

club_id = clubs['Borussia Mönchengladbach']
player_info_link = (f'https://httpget.distribution.production.datahub-sts.de/DeliveryPlatform/REST/PullOnce/datahub'
                    f'-ftp1-plus-2222/DFL-01.05-Stammdaten-Personen_Spieler/{club_id}_{season_id}')

player_info_response = requests.get(player_info_link)
player_info_xml_data = player_info_response.text
player_info_soup = BeautifulSoup(player_info_xml_data, 'xml')
players = {
    x['ObjectId']: {
        'Name': f"{x['PlayerAlias']}" if 'PlayerAlias' in x.attrs else f"{x['FirstName'][0]}. {x['LastName']}",
        'ShirtNumber': x['ShirtNumber']
    }
    for x in player_info_soup.find_all('Object')
    if not 'LeaveDate' in x.attrs and x.get('PrimaryPool') == 'true'
}
