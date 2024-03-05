import pandas as pd
from IPython.display import display
import TracabModules.External.apiFunctions as af


login_url = 'https://data.voetbaldatacentre.nl/api/login'
creds = '{"username": "chryonhego@archimedict.nl", "password": "34$h$kKs8y9Gqadp"}'
token = af.get_token(login_url, creds)
lineups = af.get_both_lineups(token, 'M335374348')

test = pd.concat([lineups[0], lineups[1]], axis=1)
display(test.to_string())