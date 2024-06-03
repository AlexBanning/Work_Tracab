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

import pandas as pd
import numpy as np
import os
import sqlite3 as sql
from TracabModules.Internal.database import create_team_stats_table, print_stats_table, create_avg_stats_table
from TracabModules.Internal.tools import get_club_id_mapping

"""
Club Mappings
"""

team_info_path = r'N:\07_QC\Alex\Databases\Team_Infos\BL1'
club_mapping = get_club_id_mapping(team_info_path, league='bl1')


"""
Database cunstruction
"""
# Specify match directory
data_path = r'N:\01_Tracking-Data\Season_23-24\52 - 2.Bundesliga 2_BL'
# List all MD folders
contents = os.listdir(data_path)


for md in contents:
    print(md)
    match_folders = os.listdir(f'{data_path}\\{md}')
    for match in match_folders:
        create_team_stats_table(matchday=md, path=data_path, match=match)

"""
Construction of league-wide stats overviews 
"""
avg_stats = create_avg_stats_table(club_mapping, league='bl1', db_update=False, data=True)

"""
Get League Stats to create printable tables
"""
league = 'bl1'
print_stats_table(league=league, kpi='Num. Sprints', logo_path=r'C:\Users\a.banning\PycharmProjects\Work_Tracab')
