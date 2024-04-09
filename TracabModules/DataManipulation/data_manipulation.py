"""
Functions that use any data or data output and return or calculate values out of them.
"""


class GatewayKPIs:

    def get_tf08_kpis(self, tf08_data):
        home_team = tf08_data['Periods'][0]['HomeTeam']['TeamName']
        home_dist = tf08_data['Periods'][0]['HomeTeam']['Distance']
        away_team = tf08_data['Periods'][0]['AwayTeam']['TeamName']
        away_dist = tf08_data['Periods'][0]['AwayTeam']['Distance']

        return {home_team: home_dist, away_team: away_dist}


