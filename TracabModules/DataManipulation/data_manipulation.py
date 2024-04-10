"""
Functions that use any data or data output and return or calculate values out of them.
"""
import numpy as np

class GatewayKPIs:

    def get_tf08_kpis(self, tf08_data):
        home_team = tf08_data['Periods'][0]['HomeTeam']['TeamName']
        home_dist = np.round(tf08_data['Periods'][0]['HomeTeam']['Distance'] / 1000,2)
        home_possession = tf08_data['Periods'][0]['HomeTeam']['PossessionData']['PossessionPercentage']
        away_team = tf08_data['Periods'][0]['AwayTeam']['TeamName']
        away_dist = np.round(tf08_data['Periods'][0]['AwayTeam']['Distance'] / 1000,2)
        away_possession = tf08_data['Periods'][0]['AwayTeam']['PossessionData']['PossessionPercentage']

        return {home_team: {'Distance': home_dist, 'Possession': home_possession},
                away_team: {'Distance': away_dist, 'Possession': away_possession}}


