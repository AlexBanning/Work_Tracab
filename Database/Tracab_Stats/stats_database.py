"""
Get Stats from BL1, BL2, and MLS
1. Create one tables with all team names and team_ids
2. Create a table for each team (naming should be based on team_id)
    2.1. Fetch distances out of each match of this team and insert them into the team table
3. Create a league_table that containts the avg distance of each team of the running season
"""

"""
1.
"""
from pathlib import Path
from TracabModules.Internal.database import create_team_stats_table, print_stats_table, create_avg_stats_table
from TracabModules.Internal.tools import get_club_id_mapping
from TracabModules.Internal.gamelog_functions import get_player_name, get_gamelog_info
import sqlite3 as sql
import pandas as pd
from xml.dom.minidom import parse
import logging

"""
Club Mappings
"""

team_info_path = Path(r'N:\07_QC\Alex\Databases\Team_Infos\MLS')
club_mapping = get_club_id_mapping(team_info_path, league='mls')

"""
Database cunstruction
 - Ask user which matchdays to update the database tables with
"""
# Specify match directory
data_path = Path(r'N:\01_Tracking-Data\Season_23-24\1 - MLS')
# List all MD folders

choice = input('Update whole season or only certain MDs? \n'
               '- season \n'
               '1 MD1 \n'
               '2 MD2 \n'
               '... \n')

# Create drop-down list from which the user can choose which matchday to update. Only those for which NAS-Folders
# already have been created, as this is a condition to be able to update the DB anyway.
# Users choice should be based on the existing_md_list

existing_md_list = [p.name for p in data_path.iterdir() if p.is_dir() and 'MD' in p.name]

if choice == '-':
    data_path = Path(r'N:\01_Tracking-Data\Season_23-24\1 - MLS')
    for md in data_path.iterdir():
        if md.is_dir() and 'MD' in md.name:
            for match in md.iterdir():
                print(match)
                create_team_stats_table(league='mls', match_folder=match)
else:
    data_path = Path(fr'N:\01_Tracking-Data\Season_23-24\1 - MLS\MD{choice}')
    for match in data_path.iterdir():
        print(match)
        create_team_stats_table(league='mls', match_folder=match)

"""
Construction of league-wide stats overviews 
"""
avg_stats = create_avg_stats_table(club_mapping, league='mls', season=2024, db_update=True, data=True)

"""
Get League Stats to create printable tables
"""
print_stats_table(league='mls', kpi='Num. SpeedRuns', season=2024,
                  logo_path=r'C:\Users\a.banning\PycharmProjects\Work_Tracab\TeamLogos\MLS_Logos')

"""
Get stats from a team
"""
league = 'bl1'
season = 2023
team_id = 16
with sql.connect(f'N:\\07_QC\\Alex\\Databases\\{league}_stats.db') as conn:
    query = f"SELECT * FROM '{team_id}' WHERE Season = {season}"
    team_stats = pd.read_sql_query(query, conn)

"""
Deleting a table
"""


def delete_table(db_path, table_name):
    """
    Delete a table from the database.

    :param db_path: Path to the SQLite database.
    :param table_name: Name of the table to delete.
    """
    with sql.connect(db_path) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            print(f"Table '{table_name}' has been deleted.")
        except sql.DatabaseError as e:
            print(f"Error deleting table {table_name}: {e}")


# Example usage:
db_path = 'N:\\07_QC\\Alex\\Databases\\bl2_stats.db'
table_name = 'league_overview'
delete_table(db_path, table_name)

"""
Eredivisie
"""
logging.basicConfig(filename='stats_log.log', level=logging.INFO, format='%(asctime)s - %(message)s')

league = 'eredivisie'
path = Path(r'N:\01_Tracking-Data\Season_23-24\9 - Eredivisie')
for md in path.iterdir():
    if not md.is_dir() and 'MD' in md.name:
        continue

    for match_folder in md.iterdir():
        print(f'Currently working on {match_folder}')

        players_data_home = []
        players_data_away = []

        observed_path = match_folder / 'Validated'
        gamelog = [p for p in observed_path.iterdir() if p.is_file() and 'Gamelog' in p.name][0]
        gamelog_info = get_gamelog_info(str(gamelog))

        resolution_path = observed_path / f'Observed/Webmonitor/Game_{gamelog_info["MatchId"]}_4/Observed/Team/Player'
        files = [p for p in resolution_path.iterdir() if p.is_file() and 'Resolution.xml' in p.name]

        team_kpis = ['Distance', 'Sprints', 'SpeedRuns']

        # Loop through all PlayerID_Resolution.xml files to fetch KPI-scores for each player
        for i, file in enumerate(files):
            try:
                xml_doc = parse(str(file))
                player_data_elements = xml_doc.getElementsByTagName('PlayerData')
                if not player_data_elements:
                    logging.error(f'PlayerData not found in {file}')
                    continue
                player_data = player_data_elements[0]
                team_id = player_data.getAttribute('TeamID')
                player_id = player_data.getAttribute('PlayerID')
                player_nr = player_data.getAttribute('PlayerNumber')
                player_name = get_player_name(str(gamelog), team_id, player_id)

                stats_elements = xml_doc.getElementsByTagName('Stats')
                if not stats_elements:
                    logging.error(f'Stats not found in {file}')
                    continue
                stats_element = stats_elements[-1]

                player_og_stats = []
                for kpi in team_kpis:
                    kpi_elements = stats_element.getElementsByTagName(kpi)
                    if kpi_elements:
                        player_og_stats.append(float(kpi_elements[0].childNodes[0].data))
                    else:
                        player_og_stats.append(0.0)  # Default to 0 if KPI not found

                if player_og_stats[0] == 0.0:
                    continue

                player = {
                    "TeamID": team_id,
                    "PlayerID": player_id,
                    "PlayerName": player_name,
                    "Total Distance": player_og_stats[0],
                    "Num. Sprints": player_og_stats[1],
                    "Num. SpeedRuns": player_og_stats[2]
                }

                if team_id == gamelog_info['HomeId']:
                    players_data_home.append(player)
                else:
                    players_data_away.append(player)

            except Exception as e:
                logging.error(f"Error processing file {file}: {e}")
                continue


        def aggregate_stats(players_data):
            if not players_data:
                return pd.DataFrame()
            df = pd.DataFrame(players_data)
            totals = df[['Total Distance', 'Num. Sprints', 'Num. SpeedRuns']].sum().round(2)
            return pd.DataFrame([totals])


        home_stats = aggregate_stats(players_data_home)
        away_stats = aggregate_stats(players_data_away)

        if home_stats.empty and away_stats.empty:
            logging.error(f"No valid player data found for {match_folder}")
            continue

        home_stats['Matchday'] = away_stats['Matchday'] = int(gamelog_info['Matchday'])
        home_stats['Season'] = away_stats['Season'] = gamelog_info['SeasonId']
        home_stats = home_stats[['Matchday', 'Season', 'Total Distance', 'Num. Sprints', 'Num. SpeedRuns']]
        away_stats = away_stats[['Matchday', 'Season', 'Total Distance', 'Num. Sprints', 'Num. SpeedRuns']]

        with sql.connect(f'N:\\07_QC\\Alex\\Databases\\{league}_stats.db') as conn:
            for team_stats, team_id in [(home_stats, gamelog_info['HomeId']), (away_stats, gamelog_info['AwayId'])]:
                # Check if the record already exists
                query = f"""
                SELECT 1 FROM '{team_id}' 
                WHERE Matchday = {team_stats['Matchday'].iloc[0]} 
                AND Season = '{team_stats['Season'].iloc[0]}'
                """
                result = pd.read_sql_query(query, conn)

                if result.empty:
                    team_stats.to_sql(team_id, conn, if_exists='append', index=False)
                    logging.info(
                        f'Tables have been successfully updated for IDs: {gamelog_info["HomeId"]} and {gamelog_info["AwayId"]}')
                else:
                    logging.info(
                        f"Record for team {team_id} on Matchday {team_stats['Matchday'].iloc[0]} already exists, "
                        f"skipping.")
