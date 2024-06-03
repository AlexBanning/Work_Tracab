from datetime import datetime, timedelta
import pandas as pd
from bs4 import BeautifulSoup
from xml.dom.minidom import parse
from pathlib import Path


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


def get_club_id_mapping(team_info_path, league):
    """
    Create a mapping between club id and club name and return it as a DataFrame.

    Parameters:
    team_info_path (str): The path to the directory or file that contains the team information necessary to create a club-id mapping.
    league (str): String that indicates which league should be used (e.g., 'mls', 'bl1', 'bl2').

    Returns:
    pd.DataFrame: A DataFrame containing the mapping of team IDs to team names.
    """

    if league == 'mls':
        team_info_file = [x for x in team_info_path.iterdir()][0]
        return get_mls_club_mapping(team_info_file)
    elif league in {'bl1', 'bl2'}:
        return get_bl_club_mapping(team_info_path)
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
        with team_info_file.open('r', encoding='utf-8') as fp:
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
