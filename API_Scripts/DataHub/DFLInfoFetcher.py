"""
club_id_link: f'https://httpget.distribution.production.datahub-sts.de/DeliveryPlatform/REST/PullOnce/STS1-PROD-UCT1-TEST/DFL-01.04-Stammdaten-Vereine/{season_id}_{comp_id}'
player_info_link : f'https://httpget.distribution.production.datahub-sts.de/DeliveryPlatform/REST/PullOnce/datahub-ftp1-plus-2222/DFL-01.05-Stammdaten-Personen_Spieler/{club_id}_{season_id}'

"""
import pandas as pd

from TracabModules.External.DataHub import DataHub
import requests
from bs4 import BeautifulSoup

datahub_download = DataHub()
season_id = datahub_download.season_id()
data = pd.DataFrame(columns=['ObjectId', 'ShirtNumber'])
for league in ['51', '52']:
    comp_id = datahub_download.sts_competition_id(tracab_id=league)
    club_id_link = (f'https://httpget.distribution.production.datahub-sts.de/DeliveryPlatform/REST/PullOnce/STS1-PROD-UCT1'
                    f'-TEST/DFL-01.04-Stammdaten-Vereine/{season_id}_{comp_id}')
    club_id_response = requests.get(club_id_link)
    club_id_xml_data = club_id_response.text
    club_id_soup = BeautifulSoup(club_id_xml_data, 'xml')
    club_ids = {x['LongName']: x['ClubId'] for x in club_id_soup.find_all('Club')}

    for club in club_ids:
        player_info_link = (f'https://httpget.distribution.production.datahub-sts.de/DeliveryPlatform/REST/PullOnce/datahub'
                            f'-ftp1-plus-2222/DFL-01.05-Stammdaten-Personen_Spieler/{club_ids[club]}_{season_id}')

        player_info_response = requests.get(player_info_link)
        player_info_xml_data = player_info_response.text
        player_info_soup = BeautifulSoup(player_info_xml_data, 'xml')
        club_df = pd.DataFrame(
            [{
            'ObjectId': x['ObjectId'],
            'ShirtNumber': x['ShirtNumber']}
            for x in player_info_soup.find_all('Object')
            if not 'LeaveDate' in x.attrs and x.get('PrimaryPool') == 'true']
        )
        data = pd.concat([data, club_df], axis=0)

