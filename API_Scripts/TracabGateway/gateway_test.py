from requests.structures import CaseInsensitiveDict
import requests

import pandas as pd

import socket
import struct
import json

# Create header
token = 'MGZhNjQ2ZTQ2NmQwOGFkNGE2NDYzMTlkNDFhN2FiNDUzZjgwZGIyYjhjNGNlNGMwODhmZDY1YjNmNjQ2YjdkZA=='
user_id = '360'
headers = CaseInsensitiveDict()
headers['accept'] = 'application/json'
headers['Authorization'] = 'Bearer ' + token

# Define match parameters
game_id = '13415'
vendor_id = '10'
extr_vers = '4'
data_quality = '0'
team_id = '215'

# Call fixtures and results
fixtures_url = f'https://api.tracab.com/api/fixtures/?VendorID={vendor_id}&Teams={team_id}'
r_fixtures = requests.get(fixtures_url, headers=headers)
fixtures = json.loads(r_fixtures.content.decode('utf8'))

# Create metadata URL
metadata_url = (
    f'https://api.tracab.com/api/V1/feeds/game_metadata?GameID={game_id}&VendorID={vendor_id}&ExtractionVersion={extr_vers}'
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

# Get raw data in dat file (ASCII format) and parse into seperate lists
dat_url = (f'https://api.tracab.com/api/V1/downloads/dat?GameID={game_id}&VendorID={vendor_id}'
           f'&ExtractionVersion={extr_vers}&DataQuality={data_quality}&Phase=0')
r_dat = requests.get(dat_url, headers=headers)
dat_text = r_dat.text
# Split string into data parts (framecount:playerpositions:ballinfo)
frames = dat_text.split(':')
framecount = [x.replace('\n', '') for x in frames[0::3]]
del framecount[-1]
# playerpositions
player_frames = [x for x in frames[1::3]]
players = [[y for y in x.split(';') if y != ''] for x in player_frames]
players_split = [[x.split(',') for x in frame] for frame in players]
x_pos_home = [[int(x[3]) for x in frame if x[0] == '1'] for frame in players_split]
x_pos_away = [[int(x[3]) for x in frame if x[0] == '0'] for frame in players_split]
x_pos_refs = [[int(x[3]) for x in frame if x[0] == '3'] for frame in players_split]
y_pos_home = [[int(x[4]) for x in frame if x[0] == '1'] for frame in players_split]
y_pos_away = [[int(x[4]) for x in frame if x[0] == '0'] for frame in players_split]
y_pos_refs = [[int(x[4]) for x in frame if x[0] == '3'] for frame in players_split]

# TF05 Feed (Heatmap and Formation)
tf05_url = (f'https://api.tracab.com/api/V1/feeds/tf05?GameID={game_id}&VendorID={vendor_id}'
            f'&ExtractionVersion={extr_vers}&DataQuality={data_quality}&Phase=0'
            )
r_tf05 = requests.get(tf05_url, headers=headers)
tf05_data = json.loads(r_tf05.content.decode('utf8'))

# TF09 Feed (Possession and Pass Data)
tf09_url = (f'https://api.tracab.com/api/V1/feeds/tf09?GameID={game_id}&VendorID={vendor_id}'
            f'&ExtractionVersion={extr_vers}&DataQuality={data_quality}'
            )
r_tf09 = requests.get(tf09_url, headers=headers)
tf09_data = json.loads(r_tf09.content.decode('utf8'))

# TF08 (Physical Data)
tf08_url = (f'https://api.tracab.com/api/V1/feeds/tf08?GameID={game_id}&VendorID={vendor_id}'
            f'&ExtractionVersion={extr_vers}&DataQuality={data_quality}'
            )
r_tf08 = requests.get(tf08_url, headers=headers)
tf08_data = json.loads(r_tf08.content.decode('utf8'))

# Get temporary API key for live subscription
tmp_url = f'https://api.tracab.com/api/internal/generatetempapikey'
r_tmpkey = requests.get(tmp_url, headers=headers)
tmpkey = json.loads(r_tmpkey.content.decode('utf8'))['tempApiKey']

# Define the JSON data for authentication
auth_data = {
    "TemporaryAPIKey": tmpkey,
    "ClassID": "TCMDAuthenticationRequest",
    "UserID": 360
}

# Convert JSON data to string
json_message = json.dumps(auth_data)

# Calculate the size of the JSON message
message_size = len(json_message)

# Convert the size to a 32-bit integer (4 bytes)
size_bytes = struct.pack('!I', message_size)

# Check connection with Heartbeat
heartbeat_data = {
    "ClassID": "TCMDClientHeartBeat",
}
# Convert JSON data to string
heartbeat_message = json.dumps(heartbeat_data)

# Calculate the size of the JSON message
heartbeat_message_size = len(heartbeat_message)

# Convert the size to a 32-bit integer (4 bytes)
heartbeat_size_bytes = struct.pack('!I', heartbeat_message_size)

# Send StartSubscription
startsub_data = {
    "GetLive": False,
    "GameID": 13415,
    "ClassID": "TCMDStartGameStreamSubscriptionRequest",
    "VendorID": 10,
    "OutProtocol": "ASCII"
}
# Convert JSON data to string
startsub_message = json.dumps(startsub_data)

# Calculate the size of the JSON message
startsub_message_size = len(startsub_message)

# Convert the size to a 32-bit integer (4 bytes)
startsub_size_bytes = struct.pack('!I', startsub_message_size)

# Define the host and port of the stream API
host = 'stream-api.tracab.com'
port = 37718

# Establish a connection to the stream API and send a heartbeat
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))

    # Send the size of the JSON message as a 32-bit integer
    s.sendall(size_bytes)

    # Send the JSON message
    s.sendall(json_message.encode())

    # Receive response if needed
    response = s.recv(1024)

    # Process response
    print("Response:", response.decode())

    # Send the size of the JSON message as a 34-bit integer
    s.sendall(heartbeat_size_bytes)

    # Send the JSON message
    s.sendall(heartbeat_message.encode())

    # Receive response if needed
    heartbeat_response = s.recv(1024)

    # Process response
    print("Response:", heartbeat_response.decode('iso-8859-1'))

    # Send the size of the JSON message as a 32-bit integer
    s.sendall(startsub_size_bytes)

    # Send the JSON message
    s.sendall(startsub_message.encode())

    # Receive response if needed
    startsub_response = s.recv(1024)

    # Process response
    print("Response:", startsub_response.decode('iso-8859-1'))
