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

selected_matchday = input('Please insert the matchday to update the database with or the whole season\n'
                          '1: MD1\n'
                          'x: MDx\n'
                          'Season: Whole season\n')

for md in data_path.iterdir():
    if selected_matchday != 'Season':
        if md.is_dir() and 'MD' in md.name and md.name.endswith(f'MD{selected_matchday}'):
            print(md)
            match_path = Path(f'{md}')
            for match in match_path.iterdir():
                create_team_stats_table(league='mls', match_folder=match)
    elif md.is_dir() and 'MD' in md.name:
        print(md)
        match_path = Path(f'{md}')
        for match in match_path.iterdir():
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
league = 'mls'
season = 2024
team_id = 10
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
