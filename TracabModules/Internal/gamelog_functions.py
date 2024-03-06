from xml.dom.minidom import parse


def get_player_name(gamelog, team_id, player_id):
    """
    This function aims to return the players name (in a specific format) from the gamelog
    based on team_id and player_id.
    :param gamelog: str
        String that is equal to the path of the gamelog.
    :param team_id: str
        String that is equal to the team_ID.
    :param player_id: str
        String that is equal to the player_ID.

    :return:
    player_name: str
        String that contains the player's name in the format 'Lastname, Firstname'
    """

    xml_doc = parse(gamelog)
    teams = xml_doc.getElementsByTagName('Rosters')[0].childNodes[0:2]
    team = [x for x in teams if x.attributes['TeamId'].childNodes[0].data == team_id][0]
    players = team.childNodes
    player_name = [f'{x.getElementsByTagName('LastName')[0].firstChild.data}, {
    x.getElementsByTagName('FirstName')[0].firstChild.data}' for x in players if
                   x.getElementsByTagName('PlId')[0].firstChild.data == player_id][0]

    return player_name
