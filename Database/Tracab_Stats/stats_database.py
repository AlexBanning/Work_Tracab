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

comp_id = 1

# Download the xml-file based on comp and season id
server = "213.168.127.130"
user = "Alex_Test"
password = "RobberyandLahm5%"
filename = 'Feed_01_04_basedata_clubs_MLS-SEA-0001K8_MLS-COM-00000' + str(comp_id) + '.xml'
ftp_dir = 'D3_MLS/MatchInfo/'

with ftputil.FTPHost(server, user, password) as ftp_host:
    ftp_host.chdir(ftp_dir)
    ftp_host.open(filename)
    if ftp_host.path.isfile(filename):
        ftp_host.download(filename, filename)

with open(filename, 'r', encoding='utf-8') as fp:
    data = BeautifulSoup(fp, 'xml')

club_data = data.find_all('Clubs')[0].contents[1::2]
club_mapping = pd.DataFrame([{
    'TeamId': str(x['DlProviderId']),
    'TeamName': x['ClubName']}
    for x in club_data
])
# Specify mls directory
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


def calculate_avg_total_distance(team_id):
    with sql.connect(r'N:\07_QC\Alex\bl2_team_stats.db') as conn:
        query = f"SELECT * FROM '{team_id}'"
        team_stats = pd.read_sql_query(query, conn)
        avg_distance = team_stats['TotalDistance'].mean()
    return np.round(avg_distance, 2)


# Example usage
team_id = '24'  # Replace with actual team ID
average_distance = calculate_avg_total_distance(team_id)
