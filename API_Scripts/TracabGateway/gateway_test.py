from requests.structures import CaseInsensitiveDict
import requests
import json
import pandas as pd
import numpy as np


# Create header
token = 'MGZhNjQ2ZTQ2NmQwOGFkNGE2NDYzMTlkNDFhN2FiNDUzZjgwZGIyYjhjNGNlNGMwODhmZDY1YjNmNjQ2YjdkZA=='
headers = CaseInsensitiveDict()
headers['accept'] = 'application/json'
headers['Authorization'] = 'Bearer ' + token


# Define match parameters
game_id = '2374331'
vendor_id = '5'
extr_vers = '4'
data_quality = '0'

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
players_x = [[x.split(',') for x in frame] for frame in players]
x_pos = [[int(x[3]) for x in frame] for frame in players_x]

# DF of all X positions of all players and refs
df = pd.DataFrame(x_pos)


ball_frames = [x for x in frames[2::3]]
# Create DF out of data lists
dat_dict = {'framecount': framecount, 'player_frames': player_frames, 'ball_frames': ball_frames}
dat_df = pd.DataFrame(dat_dict)


