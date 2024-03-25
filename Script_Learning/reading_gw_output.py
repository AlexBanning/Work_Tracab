import json

import pandas as pd
from floodlight.io.tracab import read_position_data_dat

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
df = pd.read_csv(r'C:\Users\a.banning\Downloads\2374244.dat', delimiter='\t')

# Using floodlight package
pos_data = read_position_data_dat(filepath_dat=r'C:\Users\alexa\Desktop\dat_file.dat',
                                  filepath_metadata=r'C:\Users\alexa\Desktop\metadata.json')