import json

import pandas as pd

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