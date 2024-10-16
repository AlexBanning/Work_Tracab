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
import sqlite3 as sql
import pandas as pd
import time
import cProfile
import pstats

"""
Club Mappings
"""

club_mapping = get_club_id_mapping(league='mls', season=2024)

"""
Database cunstruction
 - Ask user which matchdays to update the database tables with
"""
# Specify match directory
data_path = Path(r'N:\01_Tracking-Data\Season_23-24\9 - Eredivisie')
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
Single league update
"""
data_path = Path(fr'\\10.49.0.250\tracab_neu\01_Tracking-Data\Season_23-24\1 - MLS\MD1')
league = 'mls'
start_time = time.time()
for md in data_path.iterdir():
    if md.is_dir() and 'MD' in md.name:
        print(md)
    for match in data_path.iterdir():
        if match.is_dir():
            print(match)
            start_time_match = time.time()
            create_team_stats_table(league, match)
            # # Construct the profile output file path
            # profile_file = f"Stats_Logs\profile_output_MD1_{match.name}.prof"
        ###
            # # # # Create a Profile object
            # profiler = cProfile.Profile()
        ###
            # # # # Run the function within the profiler
            # profiler.enable()
            # create_team_stats_table(league, match)
            # profiler.disable()
        ###
            # # # # Dump the profiling results to a file
            # profiler.dump_stats(profile_file)
        ##
            print(f"Processed {match} in {time.time() - start_time_match:.2f} seconds\n")
            # # # Optionally, print or analyze the profile immediately
            # with open(f"Stats_Logs\profile_stats_MD1_{match.name}_new.txt", 'w') as f:
            #     p = pstats.Stats(profile_file, stream=f)
            #     p.sort_stats('cumulative').print_stats(50)
print(f"DB has been updated in {time.time() - start_time:.2f} seconds\n")

"""
Construction of league-wide stats overviews 
"""
avg_stats = create_avg_stats_table(club_mapping, league='mls', season=2024, db_update=True, data=True)

"""
Get League Stats to create printable tables
"""
print_stats_table(league='mls', kpi='Num. SpeedRuns', season=2024,
                  logo_path=r'C:\Users\alexa\PycharmProjects\Work_Tracab\TeamLogos\MLS_Logos')

"""
Get stats from a team
"""
league = 'bl2'
season = 2024
team_id = 15
with sql.connect(fr'\\10.49.0.250\tracab_neu\\07_QC\\Alex\\Databases\\{league}_stats.db') as conn:
    query = f"SELECT * FROM 'team_stats{team_id}' WHERE Season = {season}"
    team_stats = pd.read_sql_query(query, conn).sort_values(by='Matchday', ascending=True)

"""
Get stats from a player
"""
league = 'mls'
season = 2024
player_id = 4353
with sql.connect(fr'\\10.49.0.250\tracab_neu\\07_QC\\Alex\\Databases\\{league}_stats.db') as conn:
    query = f"SELECT * FROM 'player_stats'"
    player_stats = pd.read_sql_query(query, conn).sort_values(by=['DlProviderID', 'Matchday'], ascending=True)

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
db_path = fr'\\10.49.0.250\tracab_neu\\07_QC\\Alex\\Databases\\ekstraklasa_stats.db'
table_name = 'team_stats2192'
delete_table(db_path, table_name)

from TracabModules.Internal.database import DataFetcher
fetcher = DataFetcher(game_id='6197', league='mls', season='2024')
result = fetcher.fetch_data()