from datetime import datetime, timedelta
import pandas as pd
from bs4 import BeautifulSoup
from xml.dom.minidom import parse
from pathlib import Path
from lxml import etree
import logging


def is_date_in_current_week(date_str, mls=False):
    # Convert the date string to a datetime object
    date_to_check = datetime.strptime(date_str, '%Y-%m-%d')

    # Get today's date
    today = datetime.today()

    # Calculate the start date of the current week (assuming Monday is the start of the week)
    start_of_week = today - timedelta(days=today.weekday())

    # Calculate the end date of the current week
    end_of_week = start_of_week + timedelta(days=6)

    if not mls:
        # Check if the given date falls within the current week
        return start_of_week <= date_to_check <= end_of_week
    elif mls:
        # Calculate the start date of the week before the current week
        start_of_last_week = start_of_week - timedelta(days=7)

        # Check if the given date falls within the last two weeks
        return start_of_last_week <= date_to_check <= end_of_week


def get_club_id_mapping(league):
    """
    Create a mapping between club id and club name and return it as a DataFrame.

    Parameters:
    team_info_path (str): The path to the directory or file that contains the team information necessary to create a club-id mapping.
    league (str): String that indicates which league should be used (e.g., 'mls', 'bl1', 'bl2').

    Returns:
    pd.DataFrame: A DataFrame containing the mapping of team IDs to team names.
    """

    if league == 'mls':
        team_info_file = r'\\10.49.0.250\d3_mls\MatchInfo\Feed_01_04_basedata_clubs_MLS-SEA-0001K8_MLS-COM-000001.xml'
        return get_mls_club_mapping(team_info_file)
    elif league == 'bl1':
        team_info_path = r'\\10.49.0.250\deltatre\MatchInfo\51\2023\team_players'
        return get_bl_club_mapping(Path(team_info_path))
    elif league == 'bl2':
        team_info_path = r'\\10.49.0.250\deltatre\MatchInfo\52\2023\team_players'
        return get_bl_club_mapping(Path(team_info_path))
    elif league == 'eredivisie':
        team_info_file = r'\\10.49.0.250\Opta\MatchInfo\srml-9-2023-squads.xml'
        return get_ere_club_mapping(team_info_file)
    elif league == 'ekstraklasa':
        team_info_file = r'\\10.49.0.250\Keytoq\MatchInfo\main.xml'
        return get_ekstra_club_mapping(team_info_file)
    else:
        raise ValueError(f"Unsupported league: {league}")


def get_mls_club_mapping(team_info_file):
    """
    Create a club ID mapping for MLS from a given XML file.

    Parameters:
    team_info_file (Path): The path to the XML file containing team information.

    Returns:
    pd.DataFrame: A DataFrame containing the mapping of team IDs to team names.
    """
    try:
        with Path(team_info_file).open('r', encoding='utf-8') as fp:
            data = BeautifulSoup(fp, 'xml')

        club_data = data.find_all('Clubs')[0].contents[1::2]
        club_mapping = pd.DataFrame([{
            'TeamId': int(x['DlProviderId']),
            'TeamName': str(x['ClubName'])
        } for x in club_data]).sort_values(by='TeamId', ascending=True)

        return club_mapping

    except Exception as e:
        print(f"Error processing MLS team info file: {e}")
        return pd.DataFrame()


def get_bl_club_mapping(team_info_dir):
    """
    Create a club ID mapping for Bundesliga from a directory of XML files.

    Parameters:
    team_info_dir (Path): The path to the directory containing team information XML files.

    Returns:
    pd.DataFrame: A DataFrame containing the mapping of team IDs to team names.
    """
    club_mapping = []

    try:
        for file in team_info_dir.glob('*.xml'):
            xml_doc = parse(str(file))
            team_id = int(xml_doc.getElementsByTagName('team-metadata')[0].attributes['team-key'].value)
            team_name = str(xml_doc.getElementsByTagName('team-metadata')[0].childNodes[1].attributes['full'].value)
            club_mapping.append({'TeamId': team_id, 'TeamName': team_name})

        club_mapping = pd.DataFrame(club_mapping).sort_values(by='TeamId', ascending=True)
        return club_mapping

    except Exception as e:
        print(f"Error processing Bundesliga team info files: {e}")
        return pd.DataFrame()


def get_bl_player_mapping(league_id, team_id):
    """
    Create a ShirtNumber-ObjectID mapping for Bundesliga teams from an XML file.

    Parameters:
    team_info_file (Path): The path to the file containing team information.

    Returns:
    pd.DataFrame: A DataFrame containing the mapping of team IDs to team names.
    """
    team_info_file = fr'\\10.49.0.250\deltatre\MatchInfo\{league_id}\2023\team_players\team_players_{team_id}.xml'
    xml_doc = parse(team_info_file)

    player_elements = xml_doc.getElementsByTagName('player')
    player_id = [x.childNodes[1].getAttribute('player-key') for x in player_elements]
    shirt_number = [x.childNodes[1].getAttribute('uniform-number') for x in player_elements]
    name = [x.childNodes[1].childNodes[1].getAttribute('nickname') for x in player_elements]

    player_mapping = {shirt: {'ID': pid, 'Name': nm} for shirt, pid, nm in zip(shirt_number, player_id, name)}


    return player_mapping


def get_mls_player_mapping(season_id, team_id):
    info_path = Path(r'\\10.49.0.250\d3_mls\MatchInfo')
    clubs_file = info_path / f'Feed_01_04_basedata_clubs_MLS-SEA-0001K{season_id}_MLS-COM-000001.xml'

    with clubs_file.open('r', encoding='utf-8') as fp:
        data = BeautifulSoup(fp, 'xml')

    # Extract club data
    club_data = [x for x in data.find_all('Clubs')[0].contents[1::2]]
    id_mapping = {x['DlProviderId']: x['ClubId'] for x in club_data}

    # Identify the correct player file
    player_files = [x for x in info_path.iterdir() if 'MLS-SEA-0001K8_player.xml' in x.name]
    club_file = next(x for x in player_files if id_mapping[team_id] in x.name)

    # Parse the player file
    tree = etree.parse(str(club_file))
    root = tree.getroot()

    # Extract player data
    player_mapping = {
        obj.get("ShirtNumber"): {
            'ObjectId': obj.get("ObjectId"),
            'DlProviderId': obj.get("DlProviderId"),
            'Name': obj.get("ShortName"),
        }
        for obj in root.findall(".//Object")
    }

    return player_mapping


def get_opta_player_mapping(season_id, league_id, team_id):
    info_path = Path(fr'//10.49.0.250/Opta/MatchInfo/srml-{league_id}-{season_id}-squads.xml')
    tree = etree.parse(str(info_path))
    root = tree.getroot()

    team = [team for team in root.find('SoccerDocument').findall('Team') if team.get('uID') == f't{team_id}'][0].findall('Player')

    player_mapping = {
        obj.find('.//Stat[@Type="jersey_num"]').text: {
            'ID': obj.get('uID')[1:],
            'Name': obj.find('.//Name').text,
        }
        for obj in team
    }

    return player_mapping


def get_ere_club_mapping(team_info_file):
    # Open team info
    with open(team_info_file,
              encoding='utf8') as fp:
        team_data = BeautifulSoup(fp, 'xml')

    club_data = team_data.find_all('Team')
    club_mapping = pd.DataFrame([{
        'TeamId': int(x['uID'][1:]),
        'TeamName': str(x.find('Name').text)
    } for x in club_data]).sort_values(by='TeamId', ascending=True).drop_duplicates()

    return club_mapping


def get_ekstra_club_mapping(team_info_file):
    with open(team_info_file,
              encoding='utf8') as fp:
        team_data = BeautifulSoup(fp, 'xml')
    club_data = team_data.find_all('team')
    club_mapping = pd.DataFrame([{
        'TeamId': int(x['id']),
        'TeamName': str(x['name'])
    } for x in club_data]).sort_values(by='TeamId', ascending=True)

    return club_mapping


def get_ekstra_player_mapping(team_id, league):
    logging.basicConfig(filename=fr'StatsLogs\{league}stats_log.log', level=logging.INFO,
                        format='%(asctime)s - %(message)s')
    tree = etree.parse(str(r'\\10.49.0.250\\Keytoq\\MatchInfo\\main.xml'))
    root = tree.getroot()
    try:
        team = [x for x in root.findall('.//team') if x.get('id') == team_id][0]
    except IndexError:
        logging.info(f'Team {team_id} is not found inside the active club list of this league.')
        return

    player_mapping = {
        obj.get('nr'): {
            'ID': obj.get('id'),
            'Name': f'{obj.get('fname')} {obj.get('sname')}'
        }
        for obj in team.find('players').findall('player')
    }

    return player_mapping
