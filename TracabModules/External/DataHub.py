import requests
import logging
from bs4 import BeautifulSoup



class DataHub:
    def __init__(self):
        self.client_id = 'ChyronHego-2fac-9065-53ed'

    def season_id(self):
        logging.basicConfig(level=logging.INFO)
        url=(
            f'https://httpget.distribution.production.datahub-sts.de/DeliveryPlatform/REST/PullOnce/{self.client_id}/'
            f'DFL-01.07-BaseData-Season')
        # Sending a GET request
        response = requests.get(url)
        if response.status_code != 200:
            return logging.info(f'Error: {response.status_code}: {response.reason}')
        else:
            xml_data = response.text
            # Parse XML data with BeautifulSoup
            soup = BeautifulSoup(xml_data, 'xml')
            current_season_id = [x['SeasonId'] for x in soup.find_all('Season') if x['Season'] == '2023/2024'][0]

            return current_season_id

    def sts_competition_id(self, tracab_id):
        logging.basicConfig(level=logging.INFO)
        url=(
            f'https://httpget.distribution.production.datahub-sts.de/DeliveryPlatform/REST/PullOnce/{self.client_id}/'
            f'DFL-01.01-BaseData-Competition')
        # Sending a GET request
        response = requests.get(url)
        if response.status_code != 200:
            return logging.info(f'Error: {response.status_code}: {response.reason}')
        else:
            xml_data = response.text
            # Parse XML data with BeautifulSoup
            soup = BeautifulSoup(xml_data, 'xml')
            comps = soup.find_all('Competitions')[0].contents
            comp_id = [x['CompetitionId'] for x in comps[1::2] if x['DlProviderId'] == tracab_id][0]

        return comp_id

    def matchday_ids(self, season_id, comp_id):
        logging.basicConfig(level=logging.INFO)
        url_md_id = (
            f'https://httpget.distribution.production.datahub-sts.de/DeliveryPlatform/REST/PullOnce/{self.client_id}/'
            f'DFL-01.06-BaseData-Schedule/{season_id}')
        response = requests.get(url_md_id)
        if response.status_code != 200:
            return logging.info(f'Error: {response.status_code}: {response.reason}')
        else:
            xml_data = response.text
            soup = BeautifulSoup(xml_data, 'xml')
            matchday_ids = {x['MatchDay']: x['MatchDayId'] for x in soup.find_all('Fixtures')[0].contents[1::2]
                        if x['CompetitionId'] == comp_id}

        return matchday_ids

    def speeds(self, season_id, comp_id, matchday_id):
        logging.basicConfig(level=logging.INFO)
        url = (f'https://httpget.distribution.production.datahub-sts.de/DeliveryPlatform/REST/PullOnce/{self.client_id}/'
                    f'DFL-07.03.01-Ranglisten-Saison_Spieler_Positionsdaten/{season_id}_{comp_id}_{matchday_id}')
        response = requests.get(url)
        if response.status_code != 200:
            return logging.info(f'Error: {response.status_code}: {response.reason}')
        else:
            stats_xml_data = response.text
            soup = BeautifulSoup(stats_xml_data, 'xml')

            speeds = [x for x in soup.find_all('Ranking') if x['Type'] == 'MaximumSpeed'][0]

        return speeds

