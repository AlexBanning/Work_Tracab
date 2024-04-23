import requests
from bs4 import BeautifulSoup
import tkinter as tk
import pandas as pd
from tkinter import ttk


class DataHub:
    def __init__(self):
        self.client_id = 'ChyronHego-2fac-9065-53ed'

    def season_id(self):
        url=(
            f'https://httpget.distribution.production.datahub-sts.de/DeliveryPlatform/REST/PullOnce/{self.client_id}/'
            f'DFL-01.07-BaseData-Season')
        # Sending a GET request
        response = requests.get(url)
        xml_data = response.text
        # Parse XML data with BeautifulSoup
        soup = BeautifulSoup(xml_data, 'xml')
        current_season_id = [x['SeasonId'] for x in soup.find_all('Season') if x['Season'] == '2023/2024'][0]

        return current_season_id

    def sts_competition_id(self, tracab_id):
        url=(
            f'https://httpget.distribution.production.datahub-sts.de/DeliveryPlatform/REST/PullOnce/{self.client_id}/'
            f'DFL-01.01-BaseData-Competition')
        # Sending a GET request
        response = requests.get(url)
        xml_data = response.text
        # Parse XML data with BeautifulSoup
        soup = BeautifulSoup(xml_data, 'xml')
        comps = soup.find_all('Competitions')[0].contents
        comp_id = [x['CompetitionId'] for x in comps[1::2] if x['DlProviderId'] == tracab_id][0]

        return comp_id

    def matchday_ids(self, season_id, comp_id):
        url_md_id = (
            f'https://httpget.distribution.production.datahub-sts.de/DeliveryPlatform/REST/PullOnce/{self.client_id}/'
            f'DFL-01.06-BaseData-Schedule/{season_id}')
        response = requests.get(url_md_id)
        xml_data = response.text
        soup = BeautifulSoup(xml_data, 'xml')
        matchday_ids = {x['MatchDay']: x['MatchDayId'] for x in soup.find_all('Fixtures')[0].contents[1::2]
                    if x['CompetitionId'] == comp_id}

        return matchday_ids

    def speeds(self, season_id, comp_id, matchday_id):
        url = (f'https://httpget.distribution.production.datahub-sts.de/DeliveryPlatform/REST/PullOnce/{self.client_id}/'
                    f'DFL-07.03.01-Ranglisten-Saison_Spieler_Positionsdaten/{season_id}_{comp_id}_{matchday_id}')
        stats_response = requests.get(url)
        stats_xml_data = stats_response.text
        soup = BeautifulSoup(stats_xml_data, 'xml')

        speeds = [x for x in soup.find_all('Ranking') if x['Type'] == 'MaximumSpeed'][0]

        return speeds


class SpeedWindowGUI:
    def __init__(self):
        self.root = tk.Tk()

        self.root.iconbitmap("Tracab.ico")
        self.root.configure(bg='#2F4F4F')
        self.create_widgets()

    def create_widgets(self):
        self.speed_frame = tk.Frame(self.root)
        self.speed_frame.pack(fill=tk.BOTH, expand=True)

        self.root.iconbitmap("Tracab.ico")

        self.home_label = tk.Label(self.speed_frame, text="Home Team:")
        self.home_label.pack(pady=5)
        self.home_entry = tk.Entry(self.speed_frame)
        self.home_entry.pack(pady=5)

        self.away_label = tk.Label(self.speed_frame, text="Away Team:")
        self.away_label.pack(pady=5)
        self.away_entry = tk.Entry(self.speed_frame)
        self.away_entry.pack(pady=5)

        self.show_speeds_button = tk.Button(self.speed_frame, text="Show Speeds", command=self.show_speeds)
        self.show_speeds_button.pack(pady=10)

        self.notebook = ttk.Notebook(self.speed_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

    def show_speeds(self):
        home = self.home_entry.get()
        away = self.away_entry.get()

        # Here, replace with actual logic to get speeds based on home and away teams
        speeds_home = self.get_speeds(home)
        speeds_away = self.get_speeds(away)

        home_df = pd.DataFrame(list(speeds_home.items()), columns=['Name', 'Speed'])
        home_df_widget = Table(self.notebook, dataframe=home_df)
        home_df_widget.pack(fill=tk.BOTH, expand=True)

        away_df = pd.DataFrame(list(speeds_away.items()), columns=['Name', 'Speed'])
        away_df_widget = Table(self.notebook, dataframe=away_df)
        away_df_widget.pack(fill=tk.BOTH, expand=True)

    def get_speeds(self, team_name):
        datahub_download = DataHub()
        season_id = datahub_download.season_id()
        comp_id = datahub_download.sts_competition_id(tracab_id='51')
        matchday_ids = datahub_download.matchday_ids(season_id, comp_id)
        speeds = datahub_download.speeds(season_id, comp_id, matchday_ids['30'])

        speeds_data = {f"{x['PlayerFirstName'][0]}. {x['PlayerLastName']}": x['Absolute']
                       for x in speeds.find_all('ListEntry')
                       if x.contents[1]['TeamName'] == team_name}

        return speeds_data
