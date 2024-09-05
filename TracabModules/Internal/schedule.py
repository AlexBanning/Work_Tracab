import os
import ftputil
from pathlib import Path
import pandas as pd
from lxml import etree
from datetime import timedelta
from dateutil import parser

class Schedule:
    def __init__(self, comp_id: str, vendor: str, season_dir: str, server="213.168.127.130", user="Alex_Test", password="RobberyandLahm5%"):
        self.comp_id = comp_id
        self.vendor = vendor
        self.season_dir = season_dir
        self.info_dir = Path(fr"N:\\07_QC\Scripts\Schedule_script\{self.season_dir}\MatchInfo")
        self.server = server
        self.user = user
        self.password = password
        self.filename = ''
        self.ftp_dir = ''

    def _set_paths(self, season_id: str = None):
        """Set FTP directory and filename based on vendor."""
        if self.vendor == 'deltatre':
            self.filename = 'schedule.xml'
            self.ftp_dir = f'deltatre/MatchInfo/{self.comp_id}/{season_id}/schedule'
        elif self.vendor == 'FIFA':
            self.filename = f'{self.comp_id}_schedule.xml'
            self.ftp_dir = f'FIFA/{self.comp_id}/'
        elif self.vendor == 'opta':
            self.schedule_filename = f'srml-{self.comp_id}-{season_id}-results.xml'
            self.squads_filename = f'srml-{self.comp_id}-{season_id}-squads.xml'
            self.ftp_dir = 'Opta/MatchInfo'
        elif self.vendor == 'd3_mls':
            if self.comp_id == '102':
                self.filename = f'Feed_01_06_basedata_fixtures_MLS-SEA-0001K{season_id}_MLS-COM-00002U.xml'
            else:
                self.filename = f'Feed_01_06_basedata_fixtures_MLS-SEA-0001K{season_id}_MLS-COM-00000{self.comp_id}.xml'
            self.ftp_dir = r'D3_MLS/MatchInfo/STS-DataFetch'
        elif self.vendor == 'keytoq':
            self.comp_id = '55'
            self.filename = 'main.xml'
            self.ftp_dir = 'Keytoq/MatchInfo/'

    def download(self, season_id: str = None):
        """Download schedule files based on vendor."""
        self._set_paths(season_id)
        # os.makedirs(os.path.join(self.season_dir, "MatchInfo"), exist_ok=True)
        if Path.is_dir(self.info_dir):
            os.chdir(self.info_dir)

        try:
            with ftputil.FTPHost(self.server, self.user, self.password) as ftp_host:
                ftp_host.chdir(self.ftp_dir)
                if self.vendor != 'opta':
                    if ftp_host.path.isfile(self.filename):
                        ftp_host.download(self.filename, self.filename)
                else:
                    # Download additional files for 'opta'
                    ftp_host.download(self.schedule_filename, self.schedule_filename)
                    ftp_host.download(self.squads_filename, self.squads_filename)
        except FileNotFoundError:
            print('error')
        except Exception as e:
            print('error')

    def parse(self):
        """Dispatch to the appropriate parsing method based on the vendor."""
        if self.vendor == 'FIFA':
            return self._parse_fifa()
        elif self.vendor == 'deltatre':
            return self._parse_deltatre()
        elif self.vendor == 'opta':
            return self._parse_opta()
        elif self.vendor == 'd3_mls':
            return self._parse_d3_mls()
        elif self.vendor == 'keytoq':
            return self._parse_keytoq()
        else:
            print(f"No parsing method available for vendor {self.vendor}")
            return None

    # def _parse_fifa(self):
    #     # Specific parsing logic for FIFA
    #     print(f"Parsed FIFA schedule for {self.comp_id}")

    def _parse_deltatre(self):
        # Specific parsing logic for deltatre
        schedule_path = self.info_dir / Path(self.filename)
        tree = etree.parse(schedule_path)
        root = tree.getroot()
        # Get (if available) both halfs (all rounds) of a tournament, e.g. 'Hinrunde', 'Rückrunde'
        divisions = root[1][1:]

        # List to accumulate matchday DataFrames
        matchday_data = []

        # Iterate through divisions and match-days
        for div in divisions:
            match_days = div[1:]  # Get all match-days

            for md in match_days:
                # Determine the league based on comp_id
                league = ['1.Bundesliga'] * len(md) if self.comp_id == '51' else [root[0][1][1].attrib[
                                                                                      'code-name'].replace(
                    ' ', '')] * len(md)

                # Extract data for each match
                round_ids = [int(md.attrib['round-number'])] * len(md)
                match_ids = [match[0].attrib['event-key'] for match in md]
                home_teams = [match[1][0][0].attrib['full'] for match in md]
                away_teams = [match[2][0][0].attrib['full'] for match in md]
                stadiums = [match[0][0][0][0].attrib['full'] for match in md]

                # Parse dates using datetime for clarity
                dates = [
                    parser.parse(match[0].attrib['start-date-time']).strftime("%Y-%m-%d %H:%M")
                    for match in md
                ]

                # Create a DataFrame for the current match-day
                matchday_df = pd.DataFrame({
                    'Matchday': round_ids,
                    'MatchID': match_ids,
                    'KickOff': dates,
                    'Home': home_teams,
                    'Away': away_teams,
                    'League': league,
                    'Stadium': stadiums
                })

                # Append to the list of DataFrames
                matchday_data.append(matchday_df)

        # Concatenate all matchday DataFrames once at the end
        schedule = pd.concat(matchday_data, ignore_index=True)

        print(f"Parsed deltatre schedule for {self.comp_id}")
        return schedule

    def _parse_opta(self):
        # Specific parsing logic for opta
        schedule_path = self.info_dir / Path(self.schedule_filename)
        schedule_tree = etree.parse(schedule_path)
        schedule_root = schedule_tree.getroot()

        squad_path = self.info_dir / Path(self.squads_filename)
        squad_tree = etree.parse(squad_path)
        squad_root = squad_tree.getroot()

        # Create dictionary to link team_name and team_id
        teams = squad_root[0].findall('Team')
        team_names = [x.find('Name').text for x in teams]
        team_ids = [x.get('uID') for x in teams]
        team_dict = dict(zip(team_ids, team_names))

        # Create schedule
        matches = schedule_root[0].findall('MatchData')
        md = [int(x.find('MatchInfo').get('MatchDay')) for x in matches]
        match_ids = [x.get('uID')[1:] for x in matches]
        # dates = [x.find('MatchInfo').find('Date').text[:-3] for x in matches]
        dates = [
            (parser.parse(x.find('MatchInfo').find('Date').text[:-3]) + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')
            for x in matches
        ]
        stadiums = [x.find('Stat').text for x in matches]
        home_teams = [team_dict[x.findall('TeamData')[0].get('TeamRef')] for x in matches]
        away_teams = [team_dict[x.findall('TeamData')[1].get('TeamRef')] for x in matches]
        if int(self.comp_id) == 9:
            league = ['Eredivisie' for i in range(0, 306)]
        elif int(self.comp_id) == 5:
            league = ['CL' for i in range(0, 306)]
        elif int(self.comp_id) == 6:
            league = ['EL' for i in range(0, 306)]
        elif int(self.comp_id) == 1125:
            league = ['Conference League' for i in range(0, 306)]
        elif int(self.comp_id) == 646:
            league = ['W-CL' for i in range(0, 306)]

        schedule = pd.DataFrame(list(zip(md, match_ids, dates, home_teams, away_teams, league, stadiums)),
                                columns=['Matchday', 'MatchID', 'KickOff', 'Home', 'Away', 'League', 'Stadium'])
        print(f"Parsed opta schedule for {self.comp_id}")
        return schedule

    def _parse_d3_mls(self):
        # Specific parsing logic for D3 MLS
        with open(self.filename) as fp:
            # Add parsing code here
            pass
        print(f"Parsed D3 MLS schedule for {self.comp_id}")
        return pd.DataFrame()

    def _parse_keytoq(self):
        # Specific parsing logic for keytoq
        with open(self.filename) as fp:
            # Add parsing code here
            pass
        print(f"Parsed keytoq schedule for {self.comp_id}")
        return pd.DataFrame()

