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
import ftputil
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os
from xml.dom.minidom import parse
import sqlite3 as sql
import matplotlib.pyplot as plt
from plottable import ColumnDefinition, Table
from plottable.cmap import normed_cmap
from plottable.plots import image


"""
Club Mappings
"""
# Club Mapping MLS
server = "213.168.127.130"
user = "Alex_Test"
password = "RobberyandLahm5%"
filename = 'Feed_01_04_basedata_clubs_MLS-SEA-0001K8_MLS-COM-000001.xml'
ftp_dir = 'D3_MLS/MatchInfo/'

with ftputil.FTPHost(server, user, password) as ftp_host:
    ftp_host.chdir(ftp_dir)
    ftp_host.open(filename)
    if ftp_host.path.isfile(filename):
        ftp_host.download(filename, filename)

with open(f'C:\\Users\\alexa\\Desktop\\{filename}', 'r', encoding='utf-8') as fp:
    data = BeautifulSoup(fp, 'xml')

club_data = data.find_all('Clubs')[0].contents[1::2]
club_mapping = pd.DataFrame([{
    'TeamId': int(x['DlProviderId']),
    'TeamName': str(x['ClubName'])}
    for x in club_data
]).sort_values(by='TeamId', ascending=True)

# Club Mapping BL1
team_info_path = r'C:\Users\alexa\Desktop\teams_bl1'
team_info_files = os.listdir(team_info_path)

club_mapping_bl1 = []
for file in team_info_files:
    xml_doc_gamelog = parse(f'{team_info_path}\\{file}')
    team_id = int(xml_doc_gamelog.getElementsByTagName('team-metadata')[0].attributes['team-key'].value)
    team_name = str(xml_doc_gamelog.getElementsByTagName('team-metadata')[0].childNodes[1].attributes['full'].value)
    club_mapping_bl1.append({'TeamId': team_id, 'TeamName': team_name})

club_mapping_bl1 = pd.DataFrame(club_mapping_bl1).sort_values(by='TeamId', ascending=True)

# Club Mapping BL2
team_info_path = r'C:\Users\alexa\Desktop\teams_bl2'
team_info_files = os.listdir(team_info_path)

club_mapping_bl2 = []
for file in team_info_files:
    xml_doc_gamelog = parse(f'{team_info_path}\\{file}')
    team_id = int(xml_doc_gamelog.getElementsByTagName('team-metadata')[0].attributes['team-key'].value)
    team_name = str(xml_doc_gamelog.getElementsByTagName('team-metadata')[0].childNodes[1].attributes['full'].value)
    club_mapping_bl2.append({'TeamId': team_id, 'TeamName': team_name})

club_mapping_bl2 = pd.DataFrame(club_mapping_bl2).sort_values(by='TeamId', ascending=True)

"""
Database cunstruction
"""
# Specify match directory
bl1_path = r'N:\01_Tracking-Data\Season_23-24\52 - 2.Bundesliga 2_BL'
# List all MD folders
contents = os.listdir(bl1_path)

for md in contents:
    print(md)
    match_folders = os.listdir(f'{bl1_path}\\{md}')
    for match in match_folders:
        print(match)
        try:
            os.chdir(f'{bl1_path}\\{md}\\{match}\\Observed')
        except FileNotFoundError:
            print(f'No observed folder exists for {match}!')
            continue
        try:
            gamelog = [file for file in os.listdir(os.getcwd()) if 'Gamelog' in file][0]
        except IndexError:
            print(f'The observed folder of {match} does not contain a gamelog!')
            continue
        xml_doc_gamelog = parse(gamelog)
        try:
            matchday = xml_doc_gamelog.getElementsByTagName('TracabData')[0].attributes['RoundId'].childNodes[0].data
            teams = xml_doc_gamelog.getElementsByTagName('Rosters')[0].childNodes[0:2]
            home_id = teams[0].attributes['TeamId'].childNodes[0].data
            away_id = teams[1].attributes['TeamId'].childNodes[0].data
        except TypeError:
            matchday = xml_doc_gamelog.getElementsByTagName('TracabData')[0].attributes['RoundId'].childNodes[0].data
            teams = xml_doc_gamelog.getElementsByTagName('Rosters')[0].childNodes[1:4:2]
            home_id = teams[0].attributes['TeamId'].childNodes[0].data
            away_id = teams[1].attributes['TeamId'].childNodes[0].data

        stats = f'{os.getcwd()}\\Stats\\ReportData.xml'
        xml_doc_stats = parse(stats)
        home_tdist = float(
            xml_doc_stats.getElementsByTagName('HomeTeam')[0].attributes['TotalDistance'].childNodes[0].data.split(' ')[
                0]
        )
        away_tdist = float(
            xml_doc_stats.getElementsByTagName('AwayTeam')[0].attributes['TotalDistance'].childNodes[0].data.split(' ')[
                0]
        )
        home_nsprints = int(
            xml_doc_stats.getElementsByTagName('HomeTeam')[0].attributes['TotalSprints'].childNodes[0].data
        )
        away_nsprints = int(
            xml_doc_stats.getElementsByTagName('AwayTeam')[0].attributes['TotalSprints'].childNodes[0].data
        )
        home_nspeedruns = int(
            xml_doc_stats.getElementsByTagName('HomeTeam')[0].attributes['TotalSpeedRuns'].childNodes[0].data
        )
        away_nspeedruns = int(
            xml_doc_stats.getElementsByTagName('AwayTeam')[0].attributes['TotalSpeedRuns'].childNodes[0].data
        )

        home_stats = pd.DataFrame(
            {'TeamID': home_id, 'Matchday': int(matchday), 'TotalDistance': home_tdist, 'Num. Sprints': home_nsprints,
             'Num. SpeedRuns': home_nspeedruns}, index=[0])
        away_stats = pd.DataFrame(
            {'TeamID': away_id, 'Matchday': int(matchday), 'TotalDistance': away_tdist, 'Num. Sprints': away_nsprints,
             'Num. SpeedRuns': away_nspeedruns}, index=[0])

        # Use a single database connection for all teams
        with sql.connect(r'N:\07_QC\Alex\bl2_team_stats.db') as conn:
            home_stats.to_sql(home_id, conn, if_exists='append', index=False)
            away_stats.to_sql(away_id, conn, if_exists='append', index=False)


"""
Construction of league-wide stats overviews 
"""

VALID_LEAGUES = {'bl1', 'bl2', 'mls'}
def calculate_avg_stats(team_id, league):
    if league not in VALID_LEAGUES:
        raise ValueError("results: league must be one of %r." % VALID_LEAGUES)
    with sql.connect(f'C:\\Users\\alexa\\Desktop\\Tracab_Databases\\{league}_team_stats.db') as conn:
        query = f"SELECT * FROM '{team_id}'"
        team_stats = pd.read_sql_query(query, conn)
        avg_distance = team_stats['TotalDistance'].mean()
        avg_num_sprints = team_stats['Num. Sprints'].mean()
        avg_num_speedruns = team_stats['Num. SpeedRuns'].mean()

    return {'TeamId': team_id,
            'Total Distance': np.round(avg_distance, 2),
            'Num. Sprints': np.round(avg_num_sprints, 2),
            'Num. SpeedRuns': np.round(avg_num_speedruns, 2)}


league_stats = pd.DataFrame(columns=['TeamId', 'TeamName', 'Total Distance', 'Num. Sprints', 'Num. SpeedRuns'])
for team in club_mapping.iterrows():
    average_stats = pd.DataFrame(calculate_avg_stats(team_id=team[1]['TeamId'], league='mls'), index=[0])
    average_stats['TeamName'] = team[1]['TeamName']
    league_stats = pd.concat([league_stats, average_stats])
with sql.connect(r'N:\07_QC\Alex\avg_league_stats.db') as conn:
    league_stats.to_sql('mls_stats', conn, if_exists='replace', index=False)

"""
Get League Stats to create printable tables
"""
with sql.connect(r'N:\07_QC\Alex\avg_league_stats.db') as conn:
    league = 'bl1'
    query = f"SELECT * FROM '{league}_stats'"
    team_stats = pd.read_sql_query(query, conn)
    # team_stats['Total Distance'] = np.round(team_stats['Total Distance'] / 1000,2)

    # Select relevant columns and sort by 'Total Distance' in descending order, add team logos and reorder columns
    df_sorted = team_stats[['TeamName', 'Num. SpeedRuns']].sort_values(by='Num. SpeedRuns', ascending=False)
    # Add a rank column based on the 'Total Distance'
    df_sorted['Rank'] = df_sorted['Num. SpeedRuns'].rank(method='min', ascending=False).astype(int)

    df_sorted['Logo'] = df_sorted['TeamName'].apply(
        lambda x: f'C:\\Users\\alexa\\Downloads\\BL1_Logos\\{x}.png'
    )

    df_sorted = df_sorted[['Rank', 'Logo', 'TeamName', 'Num. SpeedRuns']]

    # Create and define table characteristics
    bg_color = "#FFFFFF"
    text_color = "#000000"  # With black text

    plt.rcParams["text.color"] = text_color
    plt.rcParams["font.family"] = "monospace"

    col_defs = [
        ColumnDefinition(
            name="Rank",
            textprops={"ha": "center"},
            width=0.01,
        ),
        ColumnDefinition(
            name="Logo",
            textprops={"ha": "center", "va": "center", 'color': bg_color},
            width=0.01,
            plot_fn=image,
        ),
        ColumnDefinition(
            name="TeamName",
            textprops={"ha": "left"},
            width=0.04,
        ),
        ColumnDefinition(
            name="Num. SpeedRuns",
            textprops={"ha": "center", "weight": "bold"},
            width=0.01,
        )
        ]

    fig, ax = plt.subplots(figsize=(15, 22))
    fig.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    table = Table(
        df_sorted,
        column_definitions=col_defs,
        index_col="Rank",
        row_dividers=True,
        row_divider_kw={"linewidth": 0.5, "linestyle": (0, (1, 5))},
        footer_divider=True,
        textprops={"fontsize": 14},
        col_label_divider_kw={"linewidth": 0.5, "linestyle": "-"},
        column_border_kw={"linewidth": .5, "linestyle": "-"},
        ax=ax,
    )

    #fig.show()

    fig.savefig(
        'bl1_num_speedruns_table.png',
        facecolor=ax.get_facecolor(),
        dpi=200,
        bbox_inches="tight",
    )
