import xml.etree.ElementTree as ET
from pathlib import Path
import gspread
import pandas as pd


def parse_bl_players(path):
    squads = pd.DataFrame(columns=['TeamName', 'PlayerID', 'Jersey#', 'Playername', '# Name'])
    for squad_file in path.iterdir():
        if squad_file.is_file():
            try:
                tree = ET.parse(squad_file)
                root = tree.getroot()
                for player in root[1][1].findall('player'):
                    name = player.find('player-metadata').find('name').attrib.get('nickname', 'N/A')
                    nr_name = f"#{player.find('player-metadata').attrib.get('uniform-number', 'N/A')} {name}"
                    jersey_nr = player.find('player-metadata').attrib.get('uniform-number', 'N/A')
                    player_id = player.find('player-metadata').attrib.get('player-key', 'N/A')
                    team_name = root[1][1].find('team-metadata').find('name').attrib.get('full', 'N/A')

                    player_dict = {
                        'TeamName': team_name,
                        'PlayerID': player_id,
                        'Jersey#': jersey_nr,
                        'Playername': name,
                        '# Name': nr_name
                    }

                    squads = pd.concat([squads, pd.DataFrame(player_dict, index=[0])], ignore_index=True)
            except ET.ParseError as e:
                print(f"Error parsing {squad_file}: {e}")
    return squads


def parse_mls_players(path, season):
    squads = pd.DataFrame(columns=['TeamName', 'PlayerID', 'Jersey#', 'Playername', '# Name'])
    for filename in path.iterdir():
        if filename.is_file() and filename.name.endswith(f'MLS-SEA-0001K{season}_player.xml'):
            try:
                tree = ET.parse(filename)
                root = tree.getroot()
                players = root.find('Objects').findall('Object')
                for player in players:
                    f_name = player.attrib.get('FirstName', 'N/A')
                    l_name = player.attrib.get('LastName', 'N/A')
                    name = f"{f_name[0]}. {l_name}" if f_name != 'N/A' else 'N/A'
                    nr_name = f"#{player.attrib.get('ShirtNumber', 'N/A')} {name}"
                    jersey_nr = player.attrib.get('ShirtNumber', 'N/A')
                    player_id = player.attrib.get('DlProviderId', 'N/A')
                    team_name = player.attrib.get('ClubName', 'N/A')

                    player_dict = {
                        'TeamName': team_name,
                        'PlayerID': player_id,
                        'Jersey#': jersey_nr,
                        'Playername': name,
                        '# Name': nr_name
                    }

                    squads = pd.concat([squads, pd.DataFrame(player_dict, index=[0])], ignore_index=True)
            except ET.ParseError as e:
                print(f"Error parsing {filename}: {e}")
    return squads


choice_league = input("Which league do you want to update the players for? \n"
                      "51 - 1.Bundesliga \n"
                      "52 - 2.Bundesliga \n"
                      "1 - MLS \n")

choice_season = input('From which season shall the player-info be taken? \n'
                      'BL: 2023, 2024...\n'
                      'MLS: 8, 9... \n')

if choice_league == '51':
    league = '1.Bundesliga'
    path = Path(fr'\\10.49.0.250\deltatre\MatchInfo\51\{choice_season}\team_players')
    squads = parse_bl_players(path)

elif choice_league == '52':
    league = '2.Bundesliga'
    path = Path(fr'\\10.49.0.250\deltatre\MatchInfo\52\{choice_season}\team_players')
    squads = parse_bl_players(path)

elif choice_league == '1':
    league = 'MLS'
    path = Path(r'\\10.49.0.250\d3_mls\MatchInfo')
    squads = parse_mls_players(path, choice_season)

# Push squad to 23/24 Squads-Sheet
credentials_path = Path(r"N:\07_QC\Scripts\Schedule_script\Season23-24\schedule_push_authentification.json")
gc = gspread.oauth(credentials_filename=credentials_path)

try:
    squad_sheet = gc.open_by_key("1Og0bflU81tYhj-l-B7WhNGlOe6BLl7OWJVzH79K152o")
    try:
        worksheet = squad_sheet.worksheet(league)
    except gspread.WorksheetNotFound:
        squad_sheet.add_worksheet(title=league, rows=1000, cols=15)
        worksheet = squad_sheet.worksheet(league)
    worksheet.update([squads.columns.values.tolist()] + squads.values.tolist())
except Exception as e:
    print(f"Error updating Google Sheet: {e}")
