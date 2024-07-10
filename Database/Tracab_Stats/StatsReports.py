"""
One script to get all tables that are needed for the weekly stats reports
"""
from pathlib import Path
import sqlite3 as sql
import numpy as np
import pandas as pd
import gspread
from gspread.exceptions import WorksheetNotFound
import os
from lxml import etree
from matplotlib import pyplot as plt
from plottable import ColumnDefinition, Table
from plottable.plots import image

# Total Distances of all clubs ---------------------------------------------------------------------------------------

league = 'bl1'
season = '2023'
db_path = Path(f'N:/07_QC/Alex/Databases/{league}_stats.db')

with sql.connect(db_path) as conn:
    query = f"SELECT * FROM 'league_overview_{season}'"
    team_stats = pd.read_sql_query(query, conn)

# Adjust 'Total Distance' to kilometers and round to two decimal places
team_stats['Total Distance'] = np.round(team_stats['Total Distance'] / 1000, 2)

# Select relevant columns and sort by the specified KPI in descending order
df_sorted = team_stats[['TeamName', 'Total Distance']].sort_values(by='Total Distance', ascending=False)
df_sorted['Rank'] = df_sorted['Total Distance'].rank(method='min', ascending=False)
df_sorted['Rank'] = df_sorted['Rank'].apply(lambda x: int(x) if not pd.isna(x) else x)
df_sorted = df_sorted[['Rank', 'TeamName', 'Total Distance']]


def push_df_to_google(df, spreadsheet_id, worksheet):
    os.chdir(fr"N:\\07_QC\Scripts\Schedule_script\Season24-25\MatchInfo")
    gc = gspread.oauth(credentials_filename=
                       'schedule_push_authentification.json'
                       )

    # schedule_sheet = gc.open_by_key("14Dx1un2S9USaZX_5OyL2JALvxW4Fg18_OzJXaSuwYmc")
    stats_reports_sheet = gc.open_by_key(spreadsheet_id)
    # Attempt to fetch the worksheet if it exists
    try:
        worksheet = stats_reports_sheet.worksheet(worksheet)
    except WorksheetNotFound:
        # If worksheet doesn't exist, create it
        worksheet = stats_reports_sheet.add_worksheet(title=worksheet, rows=1000, cols=15)

    # Update or append data to the worksheet
    worksheet.clear()  # Clear existing content before updating
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

    return print(f'Data has been successfully pushed to {worksheet}')


push_df_to_google(df=df_sorted, spreadsheet_id='1eb58QR0kt8S_zTzkc9w3f-infU_wU_Pnero4WjdEn9s',
                  worksheet=f'{league}_Total_Distance')


def get_dfl_player_mapping(league_id):
    base_dir = fr'\\10.49.0.250\deltatre\MatchInfo\{league_id}\2023\team_players'
    data = []

    # Iterate over all files in the directory
    for filename in os.listdir(base_dir):
        if filename.endswith('.xml'):
            team_info_file = os.path.join(base_dir, filename)
            xml_doc = etree.parse(team_info_file)

            player_elements = xml_doc.xpath('//player')
            for player_element in player_elements:
                metadata = player_element.xpath('player-metadata')[0]
                player_key = metadata.get('player-key')
                uniform_number = metadata.get('uniform-number')
                nickname = metadata.xpath('name/@nickname')[0]

                data.append({
                    'uniform_number': uniform_number,
                    'DlProviderID': player_key,
                    'Name': nickname
                })

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)
    return df


# Top 10 Player Highspeeds --------------------------------------------------------------------------------------------
with sql.connect(db_path) as conn:
    player_query = f"SELECT * FROM 'player_stats'"
    players = pd.read_sql_query(player_query, conn)

# Sort DataFrame by 'HighSpeed' in descending order
df_sorted = players.sort_values(by='HighSpeed', ascending=False)

# Drop duplicates, keeping the first occurrence (which is the highest 'HighSpeed' due to sorting)
df_top_players = df_sorted.drop_duplicates(subset='DlProviderID', keep='first')

# Select the top 10 rows
top_10 = df_top_players.head(10)

# Get player mapping
player_mapping = get_dfl_player_mapping(league_id='51')

# Add names to top_10
top_10_with_names = pd.merge(top_10, player_mapping, left_on='DlProviderID', right_on='DlProviderID', how='left')

# Drop the 'DlProviderID' column if not needed anymore
top_10_with_names = top_10_with_names.drop(columns=['DlProviderID', 'Matchday', 'Season', 'Total Distance',
                                                    'Num. Sprints', 'Num. SpeedRuns', 'uniform_number'])

# Add a 'Rank' column based on 'HighSpeed' ranking
top_10_with_names['Rank'] = top_10_with_names['HighSpeed'].rank(method='min', ascending=False)

top_10_with_names = top_10_with_names[['Rank','Name', 'HighSpeed']]
push_df_to_google(df=top_10_with_names, spreadsheet_id='1eb58QR0kt8S_zTzkc9w3f-infU_wU_Pnero4WjdEn9s',
                  worksheet=f'{league}_High_Speeds')

# Top 10 Player Distances ---------------------------------------------------------------------------------------------
with sql.connect(db_path) as conn:
    player_query = f"SELECT * FROM 'player_stats'"
    players = pd.read_sql_query(player_query, conn)

players['Total Distance'] = np.round(players['Total Distance'] / 1000, 2)


avg_distance = players.groupby('DlProviderID')['Total Distance'].mean().round(2).reset_index()
avg_distance.columns = ['DlProviderID', 'Avg Distance']

# 2. Merge the average distance back into the original DataFrame
players = players.merge(avg_distance, on='DlProviderID')

# 3. Sort the DataFrame based on 'Total Distance' (or any other criteria)
df_sorted = players.sort_values(by='Avg Distance', ascending=False)

# Drop duplicates, keeping the first occurrence (which is the highest 'HighSpeed' due to sorting)
df_top_players = df_sorted.drop_duplicates(subset='DlProviderID', keep='first')

# Select the top 10 rows
top_10 = df_top_players.head(10)

# Get player mapping
player_mapping = get_dfl_player_mapping(league_id='51')

# Add names to top_10
top_10_with_names = pd.merge(top_10, player_mapping, left_on='DlProviderID', right_on='DlProviderID', how='left')

# Drop the 'DlProviderID' column if not needed anymore
top_10_with_names = top_10_with_names.drop(columns=['DlProviderID', 'Matchday', 'Season', 'HighSpeed',
                                                    'Num. Sprints', 'Num. SpeedRuns', 'uniform_number', 'Total Distance'])

# Add a 'Rank' column based on 'HighSpeed' ranking
top_10_with_names['Rank'] = top_10_with_names['Avg Distance'].rank(method='min', ascending=False)

top_10_with_names = top_10_with_names[['Rank', 'Name', 'Avg Distance']]
push_df_to_google(df=top_10_with_names, spreadsheet_id='1eb58QR0kt8S_zTzkc9w3f-infU_wU_Pnero4WjdEn9s',
                  worksheet=f'{league}_Total_Distance_players')
# Top 10 Player Sprints ---------------------------------------------------------------------------------------------
with sql.connect(db_path) as conn:
    player_query = f"SELECT * FROM 'player_stats'"
    players = pd.read_sql_query(player_query, conn)

players['Total Distance'] = np.round(players['Total Distance'] / 1000, 2)


avg_sprints = players.groupby('DlProviderID')['Num. Sprints'].mean().round(2).reset_index()
avg_sprints.columns = ['DlProviderID', 'Avg Sprints']

# 2. Merge the average distance back into the original DataFrame
players = players.merge(avg_sprints, on='DlProviderID')

# 3. Sort the DataFrame based on 'Total Distance' (or any other criteria)
df_sorted = players.sort_values(by='Avg Sprints', ascending=False)

# Drop duplicates, keeping the first occurrence (which is the highest 'HighSpeed' due to sorting)
df_top_players = df_sorted.drop_duplicates(subset='DlProviderID', keep='first')

# Select the top 10 rows
top_10 = df_top_players.head(10)

# Get player mapping
player_mapping = get_dfl_player_mapping(league_id='51')

# Add names to top_10
top_10_with_names = pd.merge(top_10, player_mapping, left_on='DlProviderID', right_on='DlProviderID', how='left')

# Drop the 'DlProviderID' column if not needed anymore
top_10_with_names = top_10_with_names.drop(columns=['DlProviderID', 'Matchday', 'Season', 'HighSpeed',
                                                    'Num. SpeedRuns', 'uniform_number', 'Total Distance', 'Num. Sprints'])

# Add a 'Rank' column based on 'HighSpeed' ranking
top_10_with_names['Rank'] = top_10_with_names['Avg Sprints'].rank(method='min', ascending=False)

top_10_with_names = top_10_with_names[['Rank', 'Name', 'Avg Sprints']]
push_df_to_google(df=top_10_with_names, spreadsheet_id='1eb58QR0kt8S_zTzkc9w3f-infU_wU_Pnero4WjdEn9s',
                  worksheet=f'{league}_Num._of_Sprints_players')

# Create table
# Define table characteristics
bg_color = "#052A2A"
text_color = "#127839"
plt.rcParams["text.color"] = text_color
plt.rcParams["font.family"] = "monospace"

col_defs = [
    ColumnDefinition(name="Rank", textprops={"ha": "center"}, width=0.01),
    ColumnDefinition(name="Name", textprops={"ha": "center"}, width=0.02),
    ColumnDefinition(name='HighSpeed', textprops={"ha": "center", "weight": "bold"}, width=0.01)
]

# fig, ax = plt.subplots(figsize=(15, 22))
fig, ax = plt.subplots(figsize=(7.5, 8))
fig.set_facecolor(bg_color)
ax.set_facecolor(bg_color)

# Create the table
table = Table(
    top_10_with_names,
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

# Adjust layout to fit the table tightly
plt.tight_layout(pad=0.1)

# Save the figure
# output_path = Path(f'N:\\07_QC\\Alex\\StatsReports\\{league.upper()}') / f'{league}_{kpi.lower()}_{season}_table.png'
fig.savefig(
    f'N:\\07_QC\\Alex\\StatsReports\\Player_Highspeeds_table.png',
    facecolor=ax.get_facecolor(),
    dpi=200,
    bbox_inches="tight",
    pad_inches=0.1,  # Adjust padding as needed

)

plt.close(fig)