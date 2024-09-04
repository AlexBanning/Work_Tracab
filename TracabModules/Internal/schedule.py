import os
import ftputil
from pathlib import Path
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

    def _parse_fifa(self):
        # Specific parsing logic for FIFA
        with open(self.filename) as fp:
            data = BeautifulSoup(fp, features='html.parser')
        # Parse data into a DataFrame
        os.chdir(fr"N:\\07_QC\Scripts\Schedule_script\{season_dir}\MatchInfo")
        with open(filename) as fp:
            data = BeautifulSoup(fp, features='html.parser')

        rounds = data.find_all('tournament-round')

        # Create empty DF
        schedule = pd.DataFrame(columns=["Matchday", "MatchID", "KickOff", "Home", "Away", "League", "Stadium"])
        # Get info for all matches and update DF
        for j, round in enumerate(rounds):
            matchday = int(round["round-key"])
            fixtures = round.find_all("sports-event")
            for i, match in enumerate(fixtures):
                date = match.find("event-metadata")["start-date-time"][0:10]
                time = match.find("event-metadata")["start-date-time"][11:16]
                ko_date = (datetime.strptime(date + ' ' + time, "%Y-%m-%d %H:%M") + timedelta(hours=2)
                           ).strftime("%Y-%m-%d %H:%M")
                home = match.find_all("team")[0].find("team-metadata").find("name")["full"].encode("latin").decode(
                    "utf-8")
                away = match.find_all("team")[1].find("team-metadata").find("name")["full"].encode("latin").decode(
                    "utf-8")
                match_id = match.find("event-metadata")["event-key"]
                stadium = match.find("event-metadata").find("site").find("site-metadata").find("name")["full"].encode(
                    "latin").decode("utf-8")
                # Check which competition to add the accurate league. Info is missing in schedule.xml
                if comp_id == '285026':
                    league = 'FIFA Women WC'

                match_info = pd.DataFrame(
                    {"Matchday": matchday, "MatchID": match_id, "KickOff": ko_date, "Home": home, "Away": away,
                     "League": league, "Stadium": stadium}, index=[0])

                schedule = pd.concat([schedule, match_info])
        print(f"Parsed FIFA schedule for {self.comp_id}")
        return pd.DataFrame()  # Replace with actual parsed DataFrame

    def _parse_deltatre(self):
        # Specific parsing logic for deltatre
        with open(self.filename) as fp:
            # Add parsing code here
            pass
        print(f"Parsed deltatre schedule for {self.comp_id}")
        return pd.DataFrame()

    def _parse_opta(self):
        # Specific parsing logic for opta
        with open(self.schedule_filename) as fp:
            # Add parsing code here
            pass
        print(f"Parsed opta schedule for {self.comp_id}")
        return pd.DataFrame()

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

