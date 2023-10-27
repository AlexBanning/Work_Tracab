import ftputil
from bs4 import BeautifulSoup
from datetime import timedelta, datetime, date

def get_STSID(comp_id, home_team, away_team):
    """

    :param home_team:
    :return:
    """
    # Create a function that can download the gamestats of a single match based on the home team's name
    # Download squad xml and schedule xml to be able to map team name and team ID and get the MatchID of their match
    server = "213.168.127.130"
    user = "Alex_Test"
    password = "RobberyandLahm5%"
    filename = 'Feed_01_06_basedata_fixtures_MLS-COM-00000' + str(comp_id) + '.xml'
    # correct file: 'Feed_01_06_basedata_fixtures_MLS-SEA-0001K7_MLS-COM-000001.xml'
    ftp_dir = 'D3_MLS/MatchInfo/'
    try:
        with ftputil.FTPHost(server, user, password) as ftp_host:
            ftp_host.chdir(ftp_dir)
            ftp_host.open(filename)
            if ftp_host.path.isfile(filename):
                ftp_host.download(filename, filename)
    except:
        pass

    with open(filename) as fp:
        data = BeautifulSoup(fp, 'xml')

    # MatchIds of all matches of the home_team
    matches_schedule = data.find_all('Fixture')
    # today = '2023-10-24'
    # today = date.today().strftime('%Y-%m-%d')
    # yesterday = (date.today()- timedelta(days=1)).strftime('%Y-%m-%d')
    # yesterday = '2023-10-25'
    match_id = [x['MatchId'] for x in matches_schedule if
                str(x['HomeTeamName']) == home_team and str(x['GuestTeamName']) == away_team][0]
    date = [x['PlannedKickoffTimeCustom'][0:10] for x in matches_schedule if
                str(x['HomeTeamName']) == home_team and str(x['GuestTeamName']) == away_team][0].replace('-', '_')

    return match_id, date
