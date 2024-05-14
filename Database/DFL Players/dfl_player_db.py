import sqlite3 as sql
import pandas as pd
from TracabModules.External.DataHub import DataHub, DFLDatabase


datahub_download = DataHub()
season_id = datahub_download.season_id()
database = DFLDatabase()
# Download all necessary data for the database table, currently highspeeds and shirtnumbers
highspeed_df = database.HighSpeeds(season_id=season_id)
info_df = database.PlayerInfo(season_id=season_id)

# Merge the DFs based on the 'ObjectId' column and reorder the DF.
data = pd.merge(highspeed_df, info_df, on='ObjectId', how='left')[['League', 'Team', 'Name', 'ObjectId',
                                                                   'ShirtNumber', 'Speed']]
data['ShirtNumber'] = data['ShirtNumber'].fillna('-')

# Connect to DB
conn = sql.connect(r'N:\07_QC\Alex\DFLPlayerDatabase.db')

# Create or Update DB
data.to_sql('DFLPlayerStats', conn, if_exists='replace', index=False)


