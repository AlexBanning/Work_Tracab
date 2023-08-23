import pandas as pd
from IPython.display import display
import TracabModules.apiFunctions as af


login_url = 'https://data.voetbaldatacentre.nl/api/login'
creds = '{"username": "chryonhego@archimedict.nl", "password": "34$h$kKs8y9Gqadp"}'
token = af.get_token(login_url, creds)
lineups = af.get_both_lineups(token, 'M335374348')

home = pd.concat([lineups[0], lineups[1]], axis=1)
print('Home Team')
display(home.to_string())
away = pd.concat([lineups[2], lineups[3]], axis=1)
print(' \n \n Away Team')
display(home.to_string())
input('Press Enter to Exit;')

