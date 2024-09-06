import os
import ftputil
from pathlib import Path
import pandas as pd
from lxml import etree
from datetime import timedelta
from dateutil import parser
import logging
import gspread
logger = logging.getLogger('reports_logger')


class Schedule:
    def __init__(self, comp_id: str, vendor: str, season_id: str, season_dir: str,
                 spreadsheet_id: str, server: str, user: str, password: str) :
        self.comp_id = comp_id
        self.vendor = vendor
        self.season_id = season_id
        self.season_dir = season_dir
        self.spreadsheet_id = spreadsheet_id
        self.info_dir = Path(fr"\\10.49.0.250\\tracab_neu\07_QC\Scripts\Schedule_script\{self.season_dir}\MatchInfo")
        self.server = server
        self.user = user
        self.password = password
        self.filename = ''
        self.ftp_dir = ''

    def _set_paths(self):
        """Set FTP directory and filename based on vendor."""
        if self.vendor == 'deltatre':
            self.filename = 'schedule.xml'
            self.ftp_dir = f'deltatre/MatchInfo/{self.comp_id}/{self.season_id}/schedule'
        elif self.vendor == 'FIFA':
            self.filename = f'{self.comp_id}_schedule.xml'
            self.ftp_dir = f'FIFA/{self.comp_id}/'
        elif self.vendor == 'opta':
            self.schedule_filename = f'srml-{self.comp_id}-{self.season_id}-results.xml'
            self.squads_filename = f'srml-{self.comp_id}-{self.season_id}-squads.xml'
            self.ftp_dir = 'Opta/MatchInfo'
        elif self.vendor == 'd3_mls':
            if self.comp_id == '102':
                self.filename = f'Feed_01_06_basedata_fixtures_MLS-SEA-0001K{self.season_id}_MLS-COM-00002U.xml'
            else:
                self.filename = f'Feed_01_06_basedata_fixtures_MLS-SEA-0001K{self.season_id}_MLS-COM-00000{self.comp_id}.xml'
            self.ftp_dir = r'D3_MLS/MatchInfo/STS-DataFetch'
        elif self.vendor == 'keytoq':
            self.comp_id = '55'
            self.filename = 'main.xml'
            self.ftp_dir = 'Keytoq/MatchInfo/'

    def _download(self):
        """Download schedule files based on vendor."""
        self._set_paths()
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
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
        except ftputil.error.FTPError as e:
            logger.error(f"FTP error occurred: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

    def parse(self):
        """Dispatch to the appropriate parsing method based on the vendor."""
        self._download()

        parsers = {
            'deltatre': self._parse_deltatre,
            'opta': self._parse_opta,
            'd3_mls': self._parse_d3_mls,
            'keytoq': self._parse_keytoq,
        }

        parser_function = parsers.get(self.vendor)

        if parser_function:
            df = parser_function()
            self._push_schedule(df)
        else:
            logger.error(f"No parsing method available for vendor {self.vendor}")

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
        team_dict = {team.get('uID'): team.find('Name').text for team in squad_root[0].findall('Team')}

        # Create schedule
        matches = schedule_root[0].findall('MatchData')

        match_days = []
        match_ids = []
        dates = []
        home_teams = []
        away_teams = []
        stadiums = []

        for match in matches:
            match_info = match.find('MatchInfo')
            match_day = int(match_info.get('MatchDay'))
            match_id = match.get('uID')[1:]  # Remove the leading character

            # Parse and adjust date
            date_text = match_info.find('Date').text[:-3]
            date = (parser.parse(date_text) + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')

            stadium = match.find('Stat').text
            home_team = team_dict[match.findall('TeamData')[0].get('TeamRef')]
            away_team = team_dict[match.findall('TeamData')[1].get('TeamRef')]

            # Append data to lists
            match_days.append(match_day)
            match_ids.append(match_id)
            dates.append(date)
            home_teams.append(home_team)
            away_teams.append(away_team)
            stadiums.append(stadium)
        league_mapping = {
            9: 'Eredivisie',
            5: 'CL',
            6: 'EL',
            1125: 'Conference League',
            646: 'W-CL'
        }
        league = league_mapping.get(int(self.comp_id), 'Unknown League')
        leagues = [league] * len(matches)

        # Create the DataFrame
        schedule = pd.DataFrame({
            'Matchday': match_days,
            'MatchID': match_ids,
            'KickOff': dates,
            'Home': home_teams,
            'Away': away_teams,
            'League': leagues,
            'Stadium': stadiums
        })

        print(f"Parsed opta schedule for {self.comp_id}")
        return schedule

    def _parse_d3_mls(self):
        # Specific parsing logic for D3 MLS
        # Get all matches
        schedule_path = self.info_dir / Path(self.filename)
        tree = etree.parse(schedule_path)
        root = tree.getroot()

        fixtures = root[0].findall("Fixture")
        # Parsing the DST start and end times using dateutil.parser.parse
        dst_start = parser.parse('2024-03-31 02:00')
        dst_end = parser.parse('2024-10-27 03:00')
        # Mapping comp_id to league names using a dictionary
        league_mapping = {
            '1': 'MLS',
            '2': 'MLS PlayOffs',
            '6': 'MLS Leagues Cup',
            '102': 'U.S. Open Cup'
        }
        league = league_mapping.get(self.comp_id, 'Unknown League')

        # Create empty DF
        schedule = pd.DataFrame(
            columns=["Matchday", "MatchID", "KickOff", "Home", "Away", "League", "Stadium", "STS-ID"])
        # Get info for all matches and update DF
        for i, match in enumerate(fixtures):
            date = match.get("PlannedKickoffTime")[0:10]
            time = match.get("PlannedKickoffTime")[11:16]
            kickoff = date + ' ' + time
            ko_date_object = parser.parse(kickoff)
            if dst_start < ko_date_object < dst_end:
                ko_date_object = ko_date_object + timedelta(hours=2)
            else:
                ko_date_object = ko_date_object + timedelta(hours=1)
            kickoff = ko_date_object.strftime('%Y-%m-%d %H:%M')
            home = match.get("HomeTeamName")
            away = match.get("GuestTeamName")
            match_id = match.get("DlProviderId")
            matchday = int(match.get("MatchDay"))
            stadium = match.get("StadiumName").encode("latin").decode("utf-8")
            sts_match_id = match.get("MatchId")

            match_info = pd.DataFrame(
                {"Matchday": matchday, "MatchID": match_id, "KickOff": kickoff, "Home": home, "Away": away,
                 "League": league, "Stadium": stadium, "STS-ID": sts_match_id}, index=[0])

            schedule = pd.concat([schedule, match_info])
        print(f"Parsed D3 MLS schedule for {self.comp_id}")
        return schedule

    def _parse_keytoq(self):
        # Specific parsing logic for keytoq
        schedule_path = self.info_dir / Path(self.filename)
        tree = etree.parse(schedule_path)
        root = tree.getroot()

        matches = [x.findall('match') for x in root[0].findall('round')]

        schedule = pd.DataFrame(columns=["Matchday", "MatchID", "KickOff", "Home", "Away", "League"])
        for i, md in enumerate(matches):
            ko_date = [x.get('date') + ' ' + x.get('time') for x in md]
            home = [x.get('team_a') for x in md]
            away = [x.get('team_b') for x in md]
            matchId = [x.get('id') for x in md]
            league = ['Ekstraklasa' for x in md]
            round_id = [(i + 1) for x in md]

            match_info = pd.DataFrame(
                {"Matchday": round_id, "MatchID": matchId, "KickOff": ko_date, "Home": home, "Away": away,
                 "League": league})
            schedule = pd.concat([schedule, match_info])
        print(f"Parsed keytoq schedule for {self.comp_id}")
        return schedule

    def _push_schedule(self, df: pd.DataFrame, worksheet: str = None) -> None:
        """
        Takes in a pd.DataFrame and pushes it into the Google Sheet '23/24 Schedule'.
        :param df:
        :param worksheet:
        :param spreadsheet_id:
        :return:
        """
        # Set the worksheet name based on the DataFrame if not provided
        if worksheet is None:
            worksheet = df['League'].iloc[0]  # Set to the first value of the 'League' column
        try:
            os.chdir(fr"\\10.49.0.250\\tracab_neu\07_QC\Scripts\Schedule_script\Season24-25")
            gc = gspread.oauth(credentials_filename=
                               'schedule_push_authentification.json'
                               )

            # schedule_sheet = gc.open_by_key("14Dx1un2S9USaZX_5OyL2JALvxW4Fg18_OzJXaSuwYmc")
            spreadsheet = gc.open_by_key(self.spreadsheet_id)
            # Attempt to fetch the worksheet if it exists
            try:
                worksheet = spreadsheet.worksheet(worksheet)
            except gspread.exceptions.WorksheetNotFound:
                # If worksheet doesn't exist, create it
                worksheet = spreadsheet.add_worksheet(title=worksheet, rows=1000, cols=15)
            #
            # Replace NaN values with empty strings to avoid serialization issues
            df = df.fillna(0)
            #
            # Prepare data for update: convert DataFrame to list of lists
            data_to_update = [df.columns.values.tolist()] + df.values.tolist()
            #
            # Update or append data to the worksheet
            # worksheet.clear()  # Clear existing content before updating
            worksheet.update(data_to_update)
            #
            logger.critical(f'The data has been successfully pushed to the worksheet {worksheet}')
        except gspread.exceptions.APIError as e:
            logger.error(f"Failed to update Google Sheet: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while pushing data to Google Sheets: {e}")

