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
game_id = '2374393'
vendor_id = '5'
extr_vers = '4'
data_quality = '1'

# Create metadata URL
metadata_url = (
    f'https://api.tracab.com/api/V1/feeds/game_metadata?GameID={game_id}&VendorID={vendor_id}&ExtractionVersion={extr_vers}'
    f'&DataQuality={data_quality}')

# Send request to API
r_meta = requests.get(metadata_url, headers=headers).json()
with open(r'C:\Users\alexa\Desktop\metadata.json', 'w') as f:
    json.dump(r_meta, f)

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
dat_url = f'https://api.tracab.com/api/V1/downloads/dat?GameID={game_id}&VendorID={vendor_id}&ExtractionVersion={extr_vers}&DataQuality={data_quality}&Phase=0'
r_dat = requests.get(dat_url, headers=headers)
dat_text = r_dat.text
with open(r'C:\Users\alexa\Desktop\dat_file.dat', 'w') as f:
    f.write(dat_text)
    f.close()


