import json
import requests
import numpy as np
import pandas as pd
from requests.structures import CaseInsensitiveDict
from floodlight.io.tracab import read_position_data_dat

# Create header
token = 'MGZhNjQ2ZTQ2NmQwOGFkNGE2NDYzMTlkNDFhN2FiNDUzZjgwZGIyYjhjNGNlNGMwODhmZDY1YjNmNjQ2YjdkZA=='
headers = CaseInsensitiveDict()
headers['accept'] = 'application/json'
headers['Authorization'] = 'Bearer ' + token
# Define match parameters
game_id = '2374252'
vendor_id = '5'
extr_vers = '4'
data_quality = '1'
team_id = '215'

'''
JSON ------------------------------------------------------------------------------------------------------------------
'''
with open(r'C:\Users\a.banning\Downloads\184537.json') as f:
    d = json.load(f)

frames = pd.DataFrame(d['FrameData'])
players = frames['PlayerPositions']

example = players[2000]

home = [x for x in example if x['Team'] == 0]
away = [x for x in example if x['Team'] == 1]
refs = [x for x in example if x['Team'] == 3]

other = [x for x in example if x['Team'] != 1 and x['Team'] != 0 and x['Team'] != 3]

home_pos = pd.DataFrame([[x['X'], y['Y']] for x,y in zip(example, example) if x['Team'] == 0])


'''
DAT-File ------------------------------------------------------------------------------------------------------------------
'''

pos_data = read_position_data_dat(filepath_dat=r'C:\Users\alexa\Desktop\dat_file.dat',
                                  filepath_metadata=r'C:\Users\alexa\Desktop\metadata.json')


'''
TF05-Feed -------------------------------------------------------------------------------------------------------------
'''
tf05_url = (f'https://api.tracab.com/api/V1/feeds/tf05?GameID={game_id}&VendorID={vendor_id}'
            f'&ExtractionVersion={extr_vers}&DataQuality={data_quality}&Phase=0'
            )
r_tf05 = requests.get(tf05_url, headers=headers)
tf05_file = json.loads(r_tf05.content.decode('utf8'))

# Get heatmap data into a usable format
num_rows = 14
num_cols = 20
heatmap_data = np.array([int(digit) for digit in tf05_file['HomeTeam']['Heatmap']]).reshape(num_rows, num_cols)

'''
TF09-Feed --------------------------------------------------------------------------------------------------------------
'''
# TF09 Feed (Possession and Pass Data)
tf09_url = (f'https://api.tracab.com/api/V1/feeds/tf09?GameID={game_id}&VendorID={vendor_id}'
            f'&ExtractionVersion={extr_vers}&DataQuality={data_quality}'
            )
r_tf09 = requests.get(tf09_url, headers=headers)
tf09_data = json.loads(r_tf09.content.decode('utf8'))

'''
TF08-Feed --------------------------------------------------------------------------------------------------------------
'''
# TF08 (Physical Data)
tf08_url = (f'https://api.tracab.com/api/V1/feeds/tf08?GameID={game_id}&VendorID={vendor_id}'
            f'&ExtractionVersion={extr_vers}&DataQuality={data_quality}'
            )
r_tf08 = requests.get(tf08_url, headers=headers)
tf08_data = json.loads(r_tf08.content.decode('utf8'))

