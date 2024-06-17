import numpy as np
import pandas as pd
from pandas.errors import DatabaseError
from matplotlib import pyplot as plt
from plottable import ColumnDefinition, Table
from plottable.plots import image
from TracabModules.Internal.gamelog_functions import get_gamelog_info
from TracabModules.Internal.tracab_output import get_observed_stats, get_validated_stats
from TracabModules.Internal.tools import get_bl_player_mapping, get_mls_player_mapping, get_opta_player_mapping
from pathlib import Path
import sqlite3 as sql
import logging

"""
Add some logic to check if player AND team data already exists so if yes, the create_team_stats_table function 
simply skips to next match.
"""


def check_data_exists(db_path, team_ids, matchday, season):
    data_exists = True
    with sql.connect(db_path) as conn:
        try:
            for team_id in team_ids:
                query = f"""
                        SELECT 1 
                        FROM 'team_stats{team_id}' 
                        WHERE Matchday = {matchday} 
                        AND Season = '{season}'
                        """
                result = pd.read_sql_query(query, conn)
                if result.empty:
                    data_exists = False  # If any team_id does not have the record, return False
                else:
                    print(f"Record for team {team_id} on Matchday {matchday} and Season {season} already exists.")
        except pd.errors.DatabaseError:
            data_exists = False  # If any team_id does not have the record, return False
    return data_exists


def create_team_stats_table(league, match_folder):
    """
    :param match_folder:
    :param league:
    :return:
    """
    logging.basicConfig(filename='team_stats_log.log', level=logging.INFO, format='%(asctime)s - %(message)s')

    db_path = f'N:\\07_QC\\Alex\\Databases\\{league}_stats.db'
    if league == 'eredivisie':
        observed_path = Path(match_folder) / 'Validated'
    else:
        observed_path = Path(match_folder) / 'Observed'
    if not observed_path.exists():
        print(f'No observed folder exists for {match_folder}!')
        return

    try:
        gamelog = next(observed_path.glob('*Gamelog*'))
    except StopIteration:
        logging.info(f'The observed folder of {match_folder} does not contain a gamelog!')
        try:
            gamelog = next(Path(f'{match_folder}\\Live').glob('*Gamelog*'))
        except StopIteration:
            logging.info(f'The live folder of {match_folder} does not contain a gamelog!')
            return

    gamelog_info = get_gamelog_info(str(gamelog))
    gamelog_info['Gamelog'] = str(gamelog)
    team_ids = [gamelog_info['HomeId'], gamelog_info['AwayId']]

    if int(gamelog_info['Matchday']) == 1:
        if check_data_exists(db_path, team_ids, gamelog_info['Matchday'], gamelog_info['SeasonId']):
            return

    if not (league == 'eredivisie' or league == 'ekstraklasa'):
        # Get report statistics
        stats = f'{observed_path}\\Stats\\ReportData.xml'
        if Path(stats).exists():
            team_stats, player_stats = get_observed_stats(stats)

            team_stats['HomeStats']['Matchday'] = int(gamelog_info['Matchday'])
            team_stats['HomeStats']['Season'] = int(gamelog_info['SeasonId'])
            team_stats['AwayStats']['Matchday'] = int(gamelog_info['Matchday'])
            team_stats['AwayStats']['Season'] = int(gamelog_info['SeasonId'])

            team_stats['HomeStats'] = team_stats['HomeStats'][
                ['Matchday', 'Season', 'Total Distance', 'Num. Sprints', 'Num. '
                                                                         'SpeedRuns']]
            team_stats['AwayStats'] = team_stats['AwayStats'][
                ['Matchday', 'Season', 'Total Distance', 'Num. Sprints', 'Num. '
                                                                         'SpeedRuns']]
            with sql.connect(db_path) as conn:
                update_team_stats_table(teams_stats=team_stats, team_ids=team_ids,
                                        conn=conn)

                update_player_stats_tables(league=league, player_stats=player_stats,
                                           team_ids=team_ids, matchday=int(gamelog_info['Matchday']),
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
            home_stats, away_stats, home_player_stats, away_player_stats = get_validated_stats(
                filepath=stats, gamelog_info=gamelog_info)

            team_stats = {'HomeStats': home_stats, 'AwayStats': away_stats}
            player_stats = {'HomePlayerStats': home_player_stats, 'AwayPlayerStats': away_player_stats}
            team_stats['HomeStats']['Matchday'] = int(gamelog_info['Matchday'])
            team_stats['HomeStats']['Season'] = int(gamelog_info['SeasonId'])
            team_stats['AwayStats']['Matchday'] = int(gamelog_info['Matchday'])
            team_stats['AwayStats']['Season'] = int(gamelog_info['SeasonId'])

            team_stats['HomeStats'] = team_stats['HomeStats'][
                ['Matchday', 'Season', 'Total Distance', 'Num. Sprints', 'Num. '
                                                                         'SpeedRuns']]
            team_stats['AwayStats'] = team_stats['AwayStats'][
                ['Matchday', 'Season', 'Total Distance', 'Num. Sprints', 'Num. '
                                                                         'SpeedRuns']]

            with sql.connect(db_path) as conn:
                update_team_stats_table(teams_stats=team_stats, team_ids=team_ids,
                                        conn=conn)

                update_player_stats_tables(league=league, player_stats=player_stats,
                                           team_ids=team_ids, matchday=int(gamelog_info['Matchday']),
                                           season=int(gamelog_info['SeasonId']), conn=conn)

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


def update_team_stats_table(teams_stats, team_ids, conn):
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
    # Define the SQL templates
    sql_create_table = """
    CREATE TABLE IF NOT EXISTS team_stats{team_id} (
        Matchday INTEGER,
        Season INTEGER,
        `Total Distance` REAL,
        `Num. Sprints` INTEGER,
        `Num. SpeedRuns` INTEGER
    )
    """

    sql_insert = """
    INSERT INTO team_stats{team_id} (Matchday, Season, `Total Distance`, `Num. Sprints`, `Num. SpeedRuns`)
    VALUES (?, ?, ?, ?, ?)
    """

    # Convert DataFrame columns to tuples
    home_stats_tuples = teams_stats['HomeStats'].values.tolist()
    away_stats_tuples = teams_stats['AwayStats'].values.tolist()

    # Execute SQL statements
    with conn:
        cursor = conn.cursor()

        # Create home team stats table if it doesn't exist
        cursor.execute(sql_create_table.format(team_id=team_ids[0]))

        # Insert home team stats
        cursor.executemany(sql_insert.format(team_id=team_ids[0]), home_stats_tuples)

        # Create away team stats table if it doesn't exist
        cursor.execute(sql_create_table.format(team_id=team_ids[1]))

        # Insert away team stats
        cursor.executemany(sql_insert.format(team_id=team_ids[1]), away_stats_tuples)

    logging.info(f'Team statistics updated for teams {team_ids[0]} and {team_ids[1]}.')


def update_player_stats_tables(league, player_stats, team_ids, matchday, season, conn):
    """
    Update player statistics tables for both home and away teams.

    :param league: League identifier ('bl1' or 'bl2').
    :param player_stats: Dictionary containing 'HomePlayerStats' and 'AwayPlayerStats' DataFrames.
    :param team_ids: List containing the IDs of the home and away teams.
    :param matchday: Matchday number.
    :param season: Season identifier.
    :param conn: SQLite database connection.
    """
    logging.basicConfig(filename=fr'StatsLogs\{league}stats_log.log', level=logging.INFO,
                        format='%(asctime)s - %(message)s')

    league_id = {'bl1': '51', 'bl2': '52', 'mls': '8', 'eredivisie': '9'}.get(league)
    if not league_id:
        logging.error(f"Invalid league: {league}")
        return

    # Function to process player statistics
    def process_player_stats(stats_df, player_mapping):
        player_stats_list = []

        for _, row in stats_df.iterrows():
            try:
                if league == 'mls':
                    object_id = player_mapping[row['ShirtNumber']]['ObjectId']
                    provider_id = player_mapping[row['ShirtNumber']]['DlProviderId']
                else:
                    provider_id = player_mapping[row['ShirtNumber']]['ID']
            except KeyError:
                logging.info(
                    f"Number {row['ShirtNumber']} is not part of the team anymore. Please check to update manually.")
                continue
            if league == 'mls':
                player_stats_list.append({
                    'ObjectID': object_id,
                    'DlProviderID': provider_id,
                    'Matchday': matchday,
                    'Season': season,
                    'Total Distance': row['Total Distance'],
                    'HighSpeed': row['HighSpeed'],
                    'Num. Sprints': row['Num. Sprints'],
                    'Num. SpeedRuns': row['Num. SpeedRuns']
                })
            else:
                player_stats_list.append({
                    'DlProviderID': provider_id,
                    'Matchday': matchday,
                    'Season': season,
                    'Total Distance': row['Total Distance'],
                    'HighSpeed': row['HighSpeed'],
                    'Num. Sprints': row['Num. Sprints'],
                    'Num. SpeedRuns': row['Num. SpeedRuns']
                })

        return pd.DataFrame(player_stats_list)

    home_stats = player_stats['HomePlayerStats']
    away_stats = player_stats['AwayPlayerStats']

    # Get player mappings for both teams
    if league == 'bl1' or league == 'bl2':
        home_player_mapping = get_bl_player_mapping(league_id, team_ids[0])
        away_player_mapping = get_bl_player_mapping(league_id, team_ids[1])
    elif league == 'mls':
        home_player_mapping = get_mls_player_mapping(league_id, team_ids[0])
        away_player_mapping = get_mls_player_mapping(league_id, team_ids[1])
    elif league == 'eredivisie':
        home_player_mapping = get_opta_player_mapping(season, league_id, team_ids[0])
        away_player_mapping = get_opta_player_mapping(season, league_id, team_ids[1])

    # Process player stats for both teams
    home_player_stats_df = process_player_stats(home_stats, home_player_mapping)
    away_player_stats_df = process_player_stats(away_stats, away_player_mapping)

    # Combine home and away player stats into one DataFrame
    combined_player_stats_df = pd.concat([home_player_stats_df, away_player_stats_df], ignore_index=True)

    # Insert all player data in a single transaction
    with conn:
        combined_player_stats_df.to_sql('player_stats', conn, if_exists='append', index=False)

    logging.info(
        f"Player statistics updated for both teams {team_ids[0]} and {team_ids[1]} for Matchday {matchday} in Season {season}.")
