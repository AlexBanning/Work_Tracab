import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from plottable import ColumnDefinition, Table
from plottable.plots import image
from TracabModules.Internal.gamelog_functions import get_gamelog_info
from TracabModules.Internal.tracab_output import get_observed_stats
import os
from pathlib import Path
import sqlite3 as sql


def create_team_stats_table(matchday, path, match):
    """

    :param match:
    :param path:
    :param matchday:
    :return:
    """

    try:
        os.chdir(f'{path}\\{matchday}\\{match}\\Observed')
    except FileNotFoundError:
        print(f'No observed folder exists for {match}!')
        return
    try:
        gamelog = [file for file in os.listdir(os.getcwd()) if 'Gamelog' in file][0]
    except IndexError:
        print(f'The observed folder of {match} does not contain a gamelog!')
        return

    gamelog_info = get_gamelog_info(gamelog)

    # Get report statistics
    stats = f'{os.getcwd()}\\Stats\\ReportData.xml'
    home_stats, away_stats = get_observed_stats(stats)
    home_stats['Matchday'] = int(gamelog_info['Matchday'])
    home_stats['Season'] = str(gamelog_info['SeasonId'])
    away_stats['Matchday'] = int(gamelog_info['Matchday'])
    away_stats['Season'] = str(gamelog_info['SeasonId'])
    home_stats = home_stats[['Matchday', 'Season', 'TotalDistance', 'Num. Sprints', 'Num. SpeedRuns']]
    away_stats = away_stats[['Matchday', 'Season', 'TotalDistance', 'Num. Sprints', 'Num. SpeedRuns']]

    # Use a single database connection for all teams
    with sql.connect(r'N:\07_QC\Alex\Databases\bl1_stats.db') as conn:
        home_stats.to_sql(gamelog_info['HomeId'], conn, if_exists='append', index=False)
        away_stats.to_sql(gamelog_info['AwayId'], conn, if_exists='append', index=False)

    return print(
        f'Tables have been successfully updated for IDs: {gamelog_info['HomeId']} and {gamelog_info['AwayId']}')


def create_avg_stats_table(club_mapping, league, db_update=True, data=False):
    valid_leagues = {'bl1', 'bl2', 'mls'}

    def calculate_avg_stats(team_id, league):
        if league not in valid_leagues:
            raise ValueError("results: league must be one of %r." % valid_leagues)
        with sql.connect(f'N:\\07_QC\\Alex\\Databases\\{league}_stats.db') as conn:
            query = f"SELECT * FROM '{team_id}'"
            try:
                team_stats = pd.read_sql_query(query, conn)
                avg_distance = team_stats['TotalDistance'].mean()
                avg_num_sprints = team_stats['Num. Sprints'].mean()
                avg_num_speedruns = team_stats['Num. SpeedRuns'].mean()
            except sql.DatabaseError as e:
                print(f"Error accessing stats for team {team_id}: {e}")
                return None

            return {'TeamId': team_id,
                    'Total Distance': np.round(avg_distance, 2),
                    'Num. Sprints': np.round(avg_num_sprints, 2),
                    'Num. SpeedRuns': np.round(avg_num_speedruns, 2)}

    league_stats = pd.DataFrame(columns=['TeamId', 'TeamName', 'Total Distance', 'Num. Sprints', 'Num. SpeedRuns'])
    for idx, team in club_mapping.iterrows():
        avg_stats = pd.DataFrame(calculate_avg_stats(team_id=team['TeamId'], league='bl1'), index=[0])
        if avg_stats is not None:
            avg_stats['TeamName'] = team['TeamName']
            league_stats = pd.concat([league_stats, avg_stats])

    if db_update:
        with sql.connect(f'N:\\07_QC\\Alex\\Databases\\{league}_stats.db') as conn:
            league_stats.to_sql('league_overview', conn, if_exists='replace', index=False)

    elif data:
        return league_stats


def print_stats_table(league, kpi, logo_path):
    """
    Generate and save a statistics table for a given league and KPI.

    Parameters:
    league (str): The league name.
    kpi (str): The key performance indicator to be displayed.
    logo_path (str): The path to the directory containing team logos.
    :return:
    """
    db_path = Path(f'N:/07_QC/Alex/Databases/{league}_stats.db')
    try:
        with sql.connect(db_path) as conn:
            query = "SELECT * FROM 'league_overview'"
            team_stats = pd.read_sql_query(query, conn)
    except sql.Error as e:
        print(f"Error connecting to database: {e}")
        return

    # Adjust 'Total Distance' to kilometers and round to two decimal places
    team_stats['Total Distance'] = np.round(team_stats['Total Distance'] / 1000, 2)

    # Select relevant columns and sort by the specified KPI in descending order
    df_sorted = team_stats[['TeamName', kpi]].sort_values(by=kpi, ascending=False)
    df_sorted['Rank'] = df_sorted[kpi].rank(method='min', ascending=False).astype(int)

    # Add paths to team logos
    df_sorted['Logo'] = df_sorted['TeamName'].apply(lambda x: Path(logo_path) / f'{x}.png')
    df_sorted = df_sorted[['Rank', 'Logo', 'TeamName', kpi]]

    # Define table characteristics
    bg_color = "#FFFFFF"
    text_color = "#000000"
    plt.rcParams["text.color"] = text_color
    plt.rcParams["font.family"] = "monospace"

    col_defs = [
        ColumnDefinition(name="Rank", textprops={"ha": "center"}, width=0.01),
        ColumnDefinition(name="Logo", textprops={"ha": "center", "va": "center", 'color': bg_color}, width=0.01,
                         plot_fn=image),
        ColumnDefinition(name="TeamName", textprops={"ha": "left"}, width=0.04),
        ColumnDefinition(name=kpi, textprops={"ha": "center", "weight": "bold"}, width=0.01)
    ]

    fig, ax = plt.subplots(figsize=(15, 22))
    fig.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    # Create the table
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

    # Save the figure
    output_path = Path(os.getcwd()) / f'{league}_{kpi}_table.png'
    fig.savefig(
        output_path,
        facecolor=ax.get_facecolor(),
        dpi=200,
        bbox_inches="tight",
    )

    print(f'The table for {kpi} in the {league} has been created and saved here: {output_path}')
