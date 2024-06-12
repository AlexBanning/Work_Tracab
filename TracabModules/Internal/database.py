import numpy as np
import pandas as pd
from pandas.errors import DatabaseError
from matplotlib import pyplot as plt
from plottable import ColumnDefinition, Table
from plottable.plots import image
from TracabModules.Internal.gamelog_functions import get_gamelog_info
from TracabModules.Internal.tracab_output import get_observed_stats, get_validated_stats
from TracabModules.Internal.tools import get_bl_player_mapping
from pathlib import Path
import sqlite3 as sql
import logging

"""
Add some logic to check if player AND team data already exists so if yes, the create_team_stats_table function 
simply skips to next match.
"""
def check_data_exists(conn, team_id, matchday, season):
    data_exists = True
    try:
        query = f"""
                SELECT 1 
                FROM '{team_id}' 
                WHERE Matchday = {matchday} 
                AND Season = '{season}'
                """
        result = pd.read_sql_query(query, conn)
    except pd.errors.DatabaseError:
        data_exists = False  # If any team_id does not have the record, return False
    else:
        print(f"Record for team {team_id} on Matchday {matchday} and Season {season} already exists.")

    return data_exists


def create_team_stats_table(league, match_folder):
    """
    :param match_folder:
    :param league:
    :return:
    """
    logging.basicConfig(filename='stats_log.log', level=logging.INFO, format='%(asctime)s - %(message)s')

    db_path = f'N:\\07_QC\\Alex\\Databases\\{league}_stats.db'

    if league == 'eredivisie':
        observed_path = match_folder / 'Validated'
    else:
        observed_path = match_folder / 'Observed'
    if not observed_path.exists():
        print(f'No observed folder exists for {match_folder}!')
        return

    try:
        gamelog = next(observed_path.glob('*Gamelog*'))
    except StopIteration:
        print(f'The observed folder of {match_folder} does not contain a gamelog!')
        try:
            gamelog = next(Path(f'{match_folder}\\Live').glob('*Gamelog*'))
        except StopIteration:
            print(f'The live folder of {match_folder} does not contain a gamelog!')
            return

    gamelog_info = get_gamelog_info(str(gamelog))
    gamelog_info['Gamelog'] = str(gamelog)

    if not (league == 'eredivisie' or league == 'ekstraklasa'):
        # Get report statistics
        stats = f'{observed_path}\\Stats\\ReportData.xml'
        if Path(stats).exists():
            team_stats, player_stats = get_observed_stats(stats)

            team_stats['HomeStats']['Matchday'] = int(gamelog_info['Matchday'])
            team_stats['HomeStats']['Season'] = int(gamelog_info['SeasonId'])
            team_stats['AwayStats']['Matchday'] = int(gamelog_info['Matchday'])
            team_stats['AwayStats']['Season'] = int(gamelog_info['SeasonId'])

            home_stats = team_stats['HomeStats'][['Matchday', 'Season', 'Total Distance', 'Num. Sprints', 'Num. '
                                                                                                          'SpeedRuns']]
            away_stats = team_stats['AwayStats'][['Matchday', 'Season', 'Total Distance', 'Num. Sprints', 'Num. '
                                                                                                          'SpeedRuns']]
            with sql.connect(db_path) as conn:
                update_team_stats_table(team_stats=home_stats, team_id=gamelog_info['HomeId'],
                                        matchday=int(gamelog_info['Matchday']), season=int(gamelog_info['SeasonId']),
                                        conn=conn)
                update_team_stats_table(team_stats=away_stats, team_id=gamelog_info['AwayId'],
                                        matchday=int(gamelog_info['Matchday']), season=int(gamelog_info['SeasonId']),
                                        conn=conn)

                update_player_stats_tables(league=league, stats_df=player_stats['HomePlayerStats'],
                                           team_id=gamelog_info['HomeId'], matchday=int(gamelog_info['Matchday']),
                                           season=int(gamelog_info['SeasonId']), conn=conn)
                update_player_stats_tables(league=league, stats_df=player_stats['AwayPlayerStats'],
                                           team_id=gamelog_info['AwayId'], matchday=int(gamelog_info['Matchday']),
                                           season=int(gamelog_info['SeasonId']), conn=conn)

        elif not Path(stats).exists():
            logging.error(f'The folder {stats} does not exist!')
            return

    elif league == 'eredivisie' or league == 'ekstraklasa':
        if league == 'ekstraklasa':
            stats = observed_path / f'Webmonitor/Game_{gamelog_info["MatchId"]}_4/Observed/Team/Player'
        else:
            stats = observed_path / f'Observed/Webmonitor/Game_{gamelog_info["MatchId"]}_4/Observed/Team/Player'
        if Path(stats).exists():
            home_stats, away_stats = get_validated_stats(filepath=stats, gamelog_info=gamelog_info)
            if home_stats.empty and away_stats.empty:
                logging.error(f"No valid player data found for {match_folder}")
                return
            home_stats['Matchday'] = int(gamelog_info['Matchday'])
            home_stats['Season'] = str(gamelog_info['SeasonId'])
            away_stats['Matchday'] = int(gamelog_info['Matchday'])
            away_stats['Season'] = str(gamelog_info['SeasonId'])
            home_stats = home_stats[['Matchday', 'Season', 'Total Distance', 'Num. Sprints', 'Num. SpeedRuns']]
            away_stats = away_stats[['Matchday', 'Season', 'Total Distance', 'Num. Sprints', 'Num. SpeedRuns']]

            update_team_stats_table(league=league, team_stats=home_stats, team_id=team_ids[0])
            update_team_stats_table(league=league, team_stats=away_stats, team_id=team_ids[1])

        elif not Path(stats).exists():
            logging.error(f'The folder {stats} does not exist!')
            return


def create_avg_stats_table(club_mapping, league, season, db_update=True, data=False):
    valid_leagues = {'bl1', 'bl2', 'mls', 'eredivisie', 'ekstraklasa'}

    def calculate_avg_stats(team_id, league, season):
        if league not in valid_leagues:
            raise ValueError("results: league must be one of %r." % valid_leagues)
        with sql.connect(f'N:\\07_QC\\Alex\\Databases\\{league}_stats.db') as conn:
            query = f"SELECT * FROM '{team_id}' WHERE Season = {season}"
            try:
                team_stats = pd.read_sql_query(query, conn)
                avg_distance = team_stats['Total Distance'].mean().round(2)
                avg_num_sprints = team_stats['Num. Sprints'].mean().round(2)
                avg_num_speedruns = team_stats['Num. SpeedRuns'].mean().round(2)
            except DatabaseError as e:
                print(f"No stats available for team {team_id}: {e}")
                return {'TeamId': team_id,
                        'Total Distance': np.nan,
                        'Num. Sprints': np.nan,
                        'Num. SpeedRuns': np.nan}

            return {'TeamId': team_id,
                    'Total Distance': np.round(avg_distance, 2),
                    'Num. Sprints': np.round(avg_num_sprints, 2),
                    'Num. SpeedRuns': np.round(avg_num_speedruns, 2)}

    league_stats = pd.DataFrame(columns=['TeamId', 'TeamName', 'Total Distance', 'Num. Sprints', 'Num. SpeedRuns'])
    for idx, team in club_mapping.iterrows():
        avg_stats = pd.DataFrame(calculate_avg_stats(team_id=team['TeamId'], league=league, season=season), index=[0])
        if avg_stats is not None:
            avg_stats['TeamName'] = team['TeamName']
            league_stats = pd.concat([league_stats, avg_stats])

    if db_update:
        with sql.connect(f'N:\\07_QC\\Alex\\Databases\\{league}_stats.db') as conn:
            league_stats.to_sql(f'league_overview_{season}', conn, if_exists='replace', index=False)

    if data:
        return league_stats


def print_stats_table(league, season, kpi, logo_path):
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
            query = f"SELECT * FROM 'league_overview_{season}'"
            team_stats = pd.read_sql_query(query, conn)
    except sql.Error as e:
        print(f"Error connecting to database: {e}")
        return

    # Adjust 'Total Distance' to kilometers and round to two decimal places
    team_stats['Total Distance'] = np.round(team_stats['Total Distance'] / 1000, 2)

    # Select relevant columns and sort by the specified KPI in descending order
    df_sorted = team_stats[['TeamName', kpi]].sort_values(by=kpi, ascending=False)
    df_sorted['Rank'] = df_sorted[kpi].rank(method='min', ascending=False)
    df_sorted['Rank'] = df_sorted['Rank'].apply(lambda x: int(x) if not pd.isna(x) else x)

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
    output_path = Path(f'N:\\07_QC\\Alex\\StatsReports\\{league.upper()}') / f'{league}_{kpi}_{season}_table.png'
    fig.savefig(
        output_path,
        facecolor=ax.get_facecolor(),
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(f'The table for {kpi} in the {league} has been created and saved here: {output_path}')


def update_team_stats_table(team_stats, team_id, matchday, season, conn):
    """
    Update the team statistics table in the database for a specific team.

    Args:
        league (str): The name of the league.
        team_stats (pd.DataFrame): DataFrame containing team statistics.
        team_id (str): The ID of the team.
        gamelog_info (dict): Dictionary containing game log information.

    Returns:
        None
    """

    # if check_data_exists(conn, team_id, matchday, season):
    #     logging.info(
    #         f"Record for team {team_id} on Matchday {team_stats['Matchday'].iloc[0]} already exists, "
    #         f"skipping."
    #     )
    #     return
    # else:
    team_stats.to_sql(team_id, conn, if_exists='append', index=False)
    logging.info(
        f'Table has been successfully updated for ID: {team_id}'
    )
    return print(f'Table of team {team_id} has been updated for Matchday {team_stats['Matchday'].iloc[0]}.')


def update_player_stats_tables(league, stats_df, team_id, matchday, season, conn):
    """

    :param league:
    :param stats_df:
    :param team_id:
    :param matchday:
    :param season:
    :return:
    """
    logging.basicConfig(filename='stats_log.log', level=logging.INFO, format='%(asctime)s - %(message)s')

    league_id = {'bl1': '51', 'bl2': '52'}.get(league)
    if not league_id:
        logging.error(f"Invalid league: {league}")
        return

    info_path = Path(fr'\\10.49.0.250\deltatre\MatchInfo\{league_id}\2023\team_players\team_players_{team_id}.xml')
    player_mapping = get_bl_player_mapping(info_path)

    for _, row in stats_df.iterrows():
        try:
            player_id = player_mapping[row['ShirtNumber']]['ID']
        except KeyError:
            print(
                f'Number {row['ShirtNumber']} is not part of the team (ID: {team_id}) anymore. Please check to '
                f'update manually.')
            continue
        player_stats = pd.DataFrame({
            'Matchday': matchday,
            'Season': season,
            'Total Distance': row['Total Distance'],
            'High Speed': row['HighSpeed'],
            'Num. Sprints': row['Num. Sprints'],
            'Num. SpeedRuns': row['Num. SpeedRuns']
        }, index=[0])

        # Insert player data
        player_stats.to_sql(player_id, conn, if_exists='append', index=False)
        print(f'Data update for player {player_id}')
    print(
        f"Players for team {team_id} have been updated for Matchday {matchday} in Season {season}.")
