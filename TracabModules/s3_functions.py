import ftputil
from bs4 import BeautifulSoup
import os
from xml.dom.minidom import parse


def get_STSID(comp_id, home_team, away_team):
    """

    :param away_team:
    :param comp_id:
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


def newest(path):
    """
    Return the newest folder of all folders within a directory
    :param path: filepath as str
    :return:
        str: filepath of newest file
    """
    folders = [a for a in os.listdir(path) if
               os.path.isdir(os.path.join(path, a))]
    paths = [os.path.join(path, basename) for basename in folders]
    return max(paths, key=os.path.getctime)


def get_match_info(match_folder):
    """
    Search for necessary match information (both team names and matchday) and return them as str.
    :param match_folder:
    :return:
    """

    gamestats_path = match_folder + '\Data\Gamestats.xml'
    xml_doc = parse(gamestats_path)
    home_team_element = xml_doc.getElementsByTagName('Team')[0]
    home_team_name = str(dict(home_team_element.attributes.items())['sTeamDesc'])
    away_team_element = xml_doc.getElementsByTagName('Team')[1]
    away_team_name = str(dict(away_team_element.attributes.items())['sTeamDesc'])
    matchday = str(dict(xml_doc.getElementsByTagName('Hego')[0].attributes.items())['iRoundId'])

    return home_team_name, away_team_name, matchday
