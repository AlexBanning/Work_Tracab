from requests.structures import CaseInsensitiveDict
import requests
import json
import pandas as pd


# Create header
token = 'MGZhNjQ2ZTQ2NmQwOGFkNGE2NDYzMTlkNDFhN2FiNDUzZjgwZGIyYjhjNGNlNGMwODhmZDY1YjNmNjQ2YjdkZA=='
headers = CaseInsensitiveDict()
headers['accept'] = 'application/json'
headers['Authorization'] = 'Bearer ' + token


# Define match parameters
game_id = '2374331'
vendor_id = '5'
extr_vers = '4'
data_quality = '1'

# Create metadata URL
metadata_url = (f'https://api.tracab.com/api/V1/feeds/game_metadata?GameID={game_id}&VendorID={vendor_id}&ExtractionVersion={extr_vers}'
                f'&DataQuality={data_quality}')


# Send request to API
r_meta = requests.get(metadata_url, headers=headers).json()

# Get raw data in json-format
json_url = f'https://api.tracab.com/api/V1/downloads/tf10?GameID={game_id}&VendorID={vendor_id}&ExtractionVersion={extr_vers}&DataQuality={data_quality}&Phase=0'
r_json = requests.get(json_url, headers=headers)

# Parse the request content into a string that can be loaded as json and saved as a DF
json_file = json.loads(r_json.content.decode('utf8'))
frames = pd.DataFrame(json_file['FrameData'])
player_frames = frames['PlayerPositions']

# List of DFs for each frame
dfs = [pd.DataFrame(fr) for fr in player_frames]

# Get raw data in binary-format
bin_url = f'https://api.tracab.com/api/V1/downloads/tbf?GameID={game_id}&VendorID={vendor_id}&ExtractionVersion={extr_vers}&DataQuality={data_quality}&Phase=0'
r_bin = requests.get(bin_url, headers=headers)


# Get raw data in dat file (ASCII format)
dat_url = f'https://api.tracab.com/api/v1/downloads/dat?VendorID=5&GameID=2374331&DataQuality=0&ExtractionVersion=4'
r_dat = requests.get(dat_url, headers=headers)
dat_text = r_dat.text
# Split string into data parts (framecount:playerpositions:ballinfo)
frames = dat_text.split(':')
framecount = [x.replace('\n','') for x in frames[0::3]]
del framecount[-1]
# playerpositions
player_frames = [x for x in frames[1::3]]
players = [[y for y in x.split(';') if y != ''] for x in player_frames]
players_split = [[x.split(',') for x in frame] for frame in players]
x_pos_home = [[int(x[3]) for x in frame  if x[0] == '1'] for frame in players_split]
x_pos_away = [[int(x[3]) for x in frame  if x[0] == '0'] for frame in players_split]
x_pos_refs = [[int(x[3]) for x in frame  if x[0] == '3'] for frame in players_split]
y_pos_home = [[int(x[4]) for x in frame  if x[0] == '1'] for frame in players_split]
y_pos_away = [[int(x[4]) for x in frame  if x[0] == '0'] for frame in players_split]
y_pos_refs = [[int(x[4]) for x in frame  if x[0] == '3'] for frame in players_split]

columns_x = ['x_1', 'x_2', 'x_3', 'x_4', 'x_5', 'x_6', 'x_7', 'x_8', 'x_9', 'x_10', 'x_11']
columns_y = ['y_1', 'y_2', 'y_3', 'y_4', 'y_5', 'y_6', 'y_7', 'y_8', 'y_9', 'y_10', 'y_11']

home_x = pd.DataFrame(x_pos_home, columns=columns_x)
home_y = pd.DataFrame(y_pos_home, columns=columns_y)

# Initialize an empty list to store the merged columns
merged_columns = []

# Merge columns alternately
for x_col, y_col in zip(columns_x, columns_y):
    merged_columns.append(x_col)
    merged_columns.append(y_col)

# Select only the matching columns from home_x and home_y based on the merged pattern
merged_home = pd.concat([home_x[columns_x], home_y[columns_y]], axis=1)

# Rename columns based on the merged pattern
merged_home.columns = merged_columns


home_xy = [[(x,y) for x,y in zip(frame_x,frame_y)] for frame_x, frame_y in zip(x_pos_home,y_pos_home)]
away_xy = [[(x,y) for x,y in zip(frame_x,frame_y)] for frame_x, frame_y in zip(x_pos_away,y_pos_away)]
refs_xy = [[(x,y) for x,y in zip(frame_x,frame_y)] for frame_x, frame_y in zip(x_pos_refs,y_pos_refs)]

# DFs of all XY positions of all players and refs
df_home = pd.DataFrame(home_xy)
df_away = pd.DataFrame(away_xy)
df_refs = pd.DataFrame(refs_xy)


ball_frames = [x for x in frames[2::3]]
# Create DF out of data lists
dat_dict = {'framecount': framecount, 'player_frames': player_frames, 'ball_frames': ball_frames}
dat_df = pd.DataFrame(dat_dict)


