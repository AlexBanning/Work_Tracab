"""
One script to get all tables that are needed for the weekly stats reports
"""
from pathlib import Path
import sqlite3 as sql
import numpy as np
import pandas as pd
from TracabModules.Internal.scheduleFunctions import push_df_to_google
from TracabModules.Internal.tools import (get_dfl_player_mapping, get_mls_player_mapping, get_opta_player_mapping,
                                          get_ekstra_player_mapping)
# from matplotlib import pyplot as plt
# from plottable import ColumnDefinition, Table
from Database.Tracab_Stats.automatic_updater import setup_logging
import logging

LEAGUE_ID_MAPPING = {'mls': 1,
                     'bl1': 51,
                     'bl2': 52,
                     'eredivisie': 9,
                     'ekstraklasa': 55}

logger = logging.getLogger("reports_logger")
setup_logging(Path(r"N:/07_QC/Scripts/logging_configs/automatic_reports.json"))


# Club Stats to Google ---------------------------------------------------------------------------------------
def club_stats_to_google(league: str, season: int, kpi: str) -> None:
    db_path = Path(f'N:/07_QC/Alex/Databases/{league}_stats.db')

    with sql.connect(db_path) as conn:
        query = f"SELECT * FROM 'league_overview_{season}'"
        team_stats = pd.read_sql_query(query, conn)

    # Adjust 'Total Distance' to kilometers and round to two decimal places
    if kpi == 'Total Distance':
        team_stats[kpi] = np.round(team_stats[kpi] / 1000, 2)

    # Select relevant columns and sort by the specified KPI in descending order
    df_sorted = team_stats[['TeamName', kpi]].sort_values(by=kpi, ascending=False)
    df_sorted['Rank'] = df_sorted[kpi].rank(method='min', ascending=False)
    df_sorted['Rank'] = df_sorted['Rank'].apply(lambda x: int(x) if not pd.isna(x) else x)
    df_sorted = df_sorted[['Rank', 'TeamName', kpi]]
    kpi_sheet = kpi.replace(' ', '_')
    push_df_to_google(df=df_sorted, spreadsheet_id='1eb58QR0kt8S_zTzkc9w3f-infU_wU_Pnero4WjdEn9s',
                      worksheet=f'{league}_{kpi_sheet}')


# club_stats_to_google(league='mls', season=2024, kpi='Total Distance')


# Top 10 Players to Google --------------------------------------------------------------------------------------------
def top_ten_players_to_google(league: str, season: int, kpi: str) -> None:
    db_path = Path(f'N:/07_QC/Alex/Databases/{league}_stats.db')
    with sql.connect(db_path) as conn:
        player_query = f"SELECT * FROM 'player_stats' WHERE Season = {season}"
        players = pd.read_sql_query(player_query, conn)

    # Sort DataFrame by selected kpi in descending order
    df_sorted = players.sort_values(by=kpi, ascending=False)

    if kpi == 'HighSpeed':
        # Drop duplicates, keeping the first occurrence (which is the highest 'HighSpeed' due to sorting)
        df_top_players = df_sorted.drop_duplicates(subset='DlProviderID', keep='first')

    if kpi == 'Total Distance':
        df_sorted['Total Distance'] = np.round(players[kpi] / 1000, 2)
        avg_distance = players.groupby('DlProviderID')[kpi].mean().round(2).reset_index()
        avg_distance.columns = ['DlProviderID', 'Avg Distance']

        # 2. Merge the average distance back into the original DataFrame
        players = players.merge(avg_distance, on='DlProviderID')

        # 3. Sort the DataFrame based on 'Total Distance' (or any other criteria)
        df_sorted = players.sort_values(by='Avg Distance', ascending=False)

        # Drop duplicates, keeping the first occurrence (which is the highest kpi score due to sorting)
        df_top_players = df_sorted.drop_duplicates(subset='DlProviderID', keep='first')

    if kpi == 'Num. Sprints':
        avg_sprints = players.groupby('DlProviderID')[kpi].mean().round(2).reset_index()
        avg_sprints.columns = ['DlProviderID', 'Avg Sprints']

        # 2. Merge the average distance back into the original DataFrame
        players = players.merge(avg_sprints, on='DlProviderID')

        # 3. Sort the DataFrame based on 'Total Distance' (or any other criteria)
        df_sorted = players.sort_values(by='Avg Sprints', ascending=False)

        # Drop duplicates, keeping the first occurrence (which is the highest kpi score due to sorting)
        df_top_players = df_sorted.drop_duplicates(subset='DlProviderID', keep='first')

    # Select the top 10 rows
    top_10 = df_top_players.head(10)

    if league == 'bl1' or league == 'bl2':
        # Get player mapping
        player_mapping = get_dfl_player_mapping(league_id=LEAGUE_ID_MAPPING[league], season=season)
    elif league == 'mls':
        player_mapping = get_mls_player_mapping(season_id=season - 2016)
    elif league == 'eredivisie':
        player_mapping = get_opta_player_mapping(season_id=season, league_id=LEAGUE_ID_MAPPING[league])
    elif league == 'ekstraklasa':
        player_mapping = get_ekstra_player_mapping()

    # Add names to top_10
    top_10_with_names = pd.merge(top_10, player_mapping, left_on='DlProviderID', right_on='DlProviderID', how='left')

    # Add a 'Rank' column based on KPI ranking and drop remaining columns
    if kpi == 'Total Distance':
        top_10_with_names = top_10_with_names[['Name', 'Avg Distance']]
        top_10_with_names['Rank'] = top_10_with_names['Avg Distance'].rank(method='min', ascending=False)
        top_10_with_names = top_10_with_names[['Rank', 'Name', 'Avg Distance']]
    elif kpi == 'Num. Sprints':
        top_10_with_names = top_10_with_names[['Name', 'Avg Sprints']]
        top_10_with_names['Rank'] = top_10_with_names['Avg Sprints'].rank(method='min', ascending=False)
        top_10_with_names = top_10_with_names[['Rank', 'Name', 'Avg Sprints']]
    else:
        top_10_with_names = top_10_with_names[['Name', kpi]]
        top_10_with_names['Rank'] = top_10_with_names[kpi].rank(method='min', ascending=False)
        top_10_with_names = top_10_with_names[['Rank', 'Name', kpi]]

    kpi_sheet = kpi.replace(' ', '_')
    push_df_to_google(df=top_10_with_names, spreadsheet_id='1eb58QR0kt8S_zTzkc9w3f-infU_wU_Pnero4WjdEn9s',
                      worksheet=f'{league}_{kpi_sheet}_players')


# top_ten_players_to_google(league='bl2', season=2023, kpi='Num. Sprints')

# leagues = ['mls', 'bl1', 'bl2', 'eredivisie', 'ekstraklasa']
leagues = ['ekstraklasa']
kpis = ['Total Distance', 'Num. Sprints', 'HighSpeed']


def main() -> None:
    for league in leagues:
        season = 2024 if league == 'mls' else 2023
        for kpi in kpis:
            if kpi != 'HighSpeed':
                club_stats_to_google(league=league, season=season, kpi=kpi)
            top_ten_players_to_google(league=league, season=season, kpi=kpi)


if __name__ == '__main__':
    main()

# # Create player tables
# # Define table characteristics
# bg_color = "#052A2A"
# text_color = "#127839"
# plt.rcParams["text.color"] = text_color
# plt.rcParams["font.family"] = "monospace"
#
# col_defs = [
#     ColumnDefinition(name="Rank", textprops={"ha": "center"}, width=0.01),
#     ColumnDefinition(name="Name", textprops={"ha": "center"}, width=0.02),
#     ColumnDefinition(name='HighSpeed', textprops={"ha": "center", "weight": "bold"}, width=0.01)
# ]
#
#
#
# # fig, ax = plt.subplots(figsize=(15, 22))
# fig, ax = plt.subplots(figsize=(7.5, 8))
# fig.set_facecolor(bg_color)
# ax.set_facecolor(bg_color)
#
# # Create the table
# table = Table(
#     top_10_with_names,
#     column_definitions=col_defs,
#     index_col="Rank",
#     row_dividers=True,
#     row_divider_kw={"linewidth": 0.5, "linestyle": (0, (1, 5))},
#     footer_divider=True,
#     textprops={"fontsize": 14},
#     col_label_divider_kw={"linewidth": 0.5, "linestyle": "-"},
#     column_border_kw={"linewidth": .5, "linestyle": "-"},
#     ax=ax,
# )
#
# # Adjust layout to fit the table tightly
# plt.tight_layout(pad=0.1)
#
# # Save the figure
# # output_path = Path(f'N:\\07_QC\\Alex\\StatsReports\\{league.upper()}') / f'{league}_{kpi.lower()}_{season}_table.png'
# fig.savefig(
#     f'N:\\07_QC\\Alex\\StatsReports\\Player_Highspeeds_table.png',
#     facecolor=ax.get_facecolor(),
#     dpi=200,
#     bbox_inches="tight",
#     pad_inches=0.1,  # Adjust padding as needed
#
# )
#
# plt.close(fig)
