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

    xml_doc = parse(str(gamelog))
    teams = [x for x in xml_doc.getElementsByTagName('Rosters')[0].childNodes[0:4] if x.localName == 'HomeTeam' or
             x.localName == 'AwayTeam']
    team = [x for x in teams if x.attributes['TeamId'].childNodes[0].data == team_id][0]
    players = [x for x in team.childNodes if x.localName == 'Player']
    player_name = [
        f'{f'{x.getElementsByTagName("FirstName")[0].firstChild.data[0:1]}. ' if x.getElementsByTagName("FirstName") and x.getElementsByTagName("FirstName")[0].firstChild else ""}{
        x.getElementsByTagName("LastName")[0].firstChild.data if x.getElementsByTagName("LastName") and x.getElementsByTagName("LastName")[0].firstChild else ""}'
        for x in players if x.getElementsByTagName("PlId")[0].firstChild.data == player_id
    ][0]

    return player_name


def get_match_info_bvb(gamelog):
    """
    This function aims to fetch the TeamID, TeamName, GameID, CompID and Matchday out of a gamelog.
    :param gamelog:
    :return:
        Dict: Dictionary containing 'all' match information from the gamelog
    """
    xml_doc = parse(gamelog)
    teams = xml_doc.getElementsByTagName('Rosters')[0].childNodes[0:2]
    bvb_id = [x.attributes['TeamId'].childNodes[0].data for x in teams if
              x.attributes['TeamId'].childNodes[0].data == '18'][0]
    oppo_id = [x.attributes['TeamId'].childNodes[0].data for x in teams if
               x.attributes['TeamId'].childNodes[0].data != '18'][0]
    bvb_name = [x for x in teams if
                x.attributes['TeamId'].childNodes[0].data == bvb_id][0].attributes['Name'].childNodes[0].data
    oppo_name = [x for x in teams if
                 x.attributes['TeamId'].childNodes[0].data == oppo_id][0].attributes['Name'].childNodes[0].data

    match_id = xml_doc.getElementsByTagName('TracabData')[0].attributes['GameId'].childNodes[0].data
    matchday = xml_doc.getElementsByTagName('TracabData')[0].attributes['RoundId'].childNodes[0].data
    comp_id = xml_doc.getElementsByTagName('EnvironmentSettings')[0].attributes['CompetitionId'].childNodes[0].data

    return dict({'bvb_id': bvb_id, 'bvb_name': bvb_name, 'oppo_id': oppo_id, 'oppo_name': oppo_name,
                 'match_id': match_id, 'md': matchday, 'comp_id': comp_id})


# def get_match_info(gamelog):
#     xml_doc = parse(gamelog)
#     teams = xml_doc.getElementsByTagName('Rosters')[0].childNodes[0:2]
#     home_id = [x.attributes['TeamId'].childNodes[0].data for x in teams if
#               x.attributes['TeamId'].childNodes[0].data == '18'][0]
#     away_id = [x.attributes['TeamId'].childNodes[0].data for x in teams if
#               x.attributes['TeamId'].childNodes[0].data != '18'][0]
#     home_name = [x for x in teams if
#                 x.attributes['TeamId'].childNodes[0].data == bvb_id][0].attributes['Name'].childNodes[0].data
#     away_name = [x for x in teams if
#                 x.attributes['TeamId'].childNodes[0].data == oppo_id][0].attributes['Name'].childNodes[0].data


def get_gamelog_info(gamelog):
    """
    Get all necessary information of interest out of a Tracab gamelog.

    Parameters:
    gamelog (Path): Path to the gamelog XML file.

    Returns:
    dict: A dictionary with matchday, season ID, home team ID, and away team ID.
    """
    # Ensure gamelog is a Path object and convert to string for parsing

    # Parse the XML document
    xml_doc_gamelog = parse(str(gamelog))

    def get_element_data(tag_name, attribute_name, index=0):
        try:
            element = xml_doc_gamelog.getElementsByTagName(tag_name)[index]
            return element.attributes[attribute_name].value
        except (IndexError, KeyError, AttributeError):
            return None

    matchday = get_element_data('TracabData', 'RoundId')
    season_id = get_element_data('EnvironmentSettings', 'SeasonId')
    match_id = get_element_data('TracabData', 'GameId')

    # Handling teams data with try-except for different structures
    try:
        teams = xml_doc_gamelog.getElementsByTagName('Rosters')[0].childNodes[0:2]
        home_id = teams[0].attributes['TeamId'].childNodes[0].data
        away_id = teams[1].attributes['TeamId'].childNodes[0].data
    except TypeError:
        try:
            teams = xml_doc_gamelog.getElementsByTagName('Rosters')[0].childNodes[1:4:2]
            home_id = teams[0].attributes['TeamId'].childNodes[0].data
            away_id = teams[1].attributes['TeamId'].childNodes[0].data
        except (IndexError, KeyError, AttributeError):
            home_id = away_id = None

    return {'Matchday': matchday, 'SeasonId': season_id, 'MatchId': match_id, 'HomeId': home_id, 'AwayId': away_id}
