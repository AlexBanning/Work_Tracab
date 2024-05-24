import xml.etree.ElementTree as eT
from xml.dom.minidom import parse
from tkinter import messagebox
import sys


def write_gamestats(schedule, players, comp_iD, season_iD, vendor_iD):
    """
    Returns Match-Information in the required format of Tracab tracking software. Uses information regarding the
    playing teams. Could be expanded to also parse referee information.
    (comp_iD, season_iD, vendor_iD, match_info, home_team, away_team, hteam_players, ateam_players)

    :param comp_iD:
    :param season_iD:
    :param vendor_iD:
    :param match_info:
    :param home_team:
    :param away_team:
    :param hteam_players:
    :param ateam_players:

    :return:
    """

    for i, m in enumerate(schedule.iterrows()):
        if m[1]['Home'] and m[1]['Away']:
            home_team = {'iD': m[1]['hID'], 'name': m[1]['Home']}
            away_team = {'iD': m[1]['aID'], 'name': m[1]['Away']}
            hteam_players = [x[1] for x in players.iterrows() if x[1]['Team'] == m[1]['Home']]
            ateam_players = [x[1] for x in players.iterrows() if x[1]['Team'] == m[1]['Away']]
            match_info = {'iD': m[1]['MatchID'], 'kickOff': m[1]['KickOff'],
                          'venue': m[1]['Stadium'], 'round': m[1]['Matchday']}

            data = eT.Element('Hego')
            data.set('iGameNumber', match_info['iD'])
            data.set('dtGameBegin', match_info['kickOff'])
            data.set('iRoundId', match_info['round'])
            data.set('sRoundDescription', 'round_' + match_info['round'])
            data.set('sStadium', match_info['venue'])
            data.set('iStadiumId', '')
            data.set('sRefereeFirstName', 'Ref1')
            data.set('sRefereeLastName', 'Ref1')
            data.set('iRefereeCity', '')
            data.set('iRefereeId', '100')
            data.set('iSpectators', '')
            data.set('iCompetitionId', comp_iD)
            data.set('iSeasonId', season_iD)
            data.set('iVendorId', vendor_iD)
            htt = eT.SubElement(data, 'Team')
            htt.set('sType', 'Home')
            htt.set('iTeamId', home_team['iD'])
            htt.set('sTeamDesc', home_team['name'])
            htt.set('sTeamLongDesc', home_team['name'])
            htt.set('sCoachFirstName', '')
            htt.set('sCoachLastName', '')
            htt.set('sCoachId', '')
            hroster = eT.SubElement(htt, 'Roster')
            for i, player in enumerate(hteam_players):
                hplayer = eT.SubElement(hroster, 'Player')
                hplayer.set('iJerseyNo', str(player['Shirt Nr']))
                hplayer.set('iId', str(player['IFES Player ID']))
                hplayer.set('sLastName', player['Last Name as in Passport'].title())
                hplayer.set('sFirstName', player['First Name as in Passport'].title())
            hlineup = eT.SubElement(htt, 'Lineup')
            att = eT.SubElement(data, 'Team')
            att.set('sType', 'Away')
            att.set('iTeamId', away_team['iD'])
            att.set('sTeamDesc', away_team['name'])
            att.set('sTeamLongDesc', away_team['name'])
            att.set('sCoachFirstName', '')
            att.set('sCoachLastName', '')
            att.set('sCoachId', '')
            aroster = eT.SubElement(att, 'Roster')
            for i, player in enumerate(ateam_players):
                aplayer = eT.SubElement(aroster, 'Player')
                aplayer.set('iJerseyNo', str(player['Shirt Nr']))
                aplayer.set('iId', str(player['IFES Player ID']))
                aplayer.set('sLastName', player['Last Name as in Passport'].title())
                aplayer.set('sFirstName', player['First Name as in Passport'].title())
            alineup = eT.SubElement(att, 'Lineup')
            gstats = eT.SubElement(data, 'Gamestats')
            refs = eT.SubElement(data, 'Referees')
            ref = eT.SubElement(refs, 'Referee')
            ref.set('sFirstName', 'Ref1')
            ref.set('sLastName', 'Ref1')
            ref.set('sCity', '')
            ref.set('iId', '100')
            ref.set('vRefereeType', '0')
            ref = eT.SubElement(refs, 'Referee')
            ref.set('sFirstName', 'Ref2')
            ref.set('sLastName', 'Ref2')
            ref.set('sCity', '')
            ref.set('iId', '101')
            ref.set('vRefereeType', '1')
            ref = eT.SubElement(refs, 'Referee')
            ref.set('sFirstName', 'Ref3')
            ref.set('sLastName', 'Ref3')
            ref.set('sCity', '')
            ref.set('iId', '102')
            ref.set('vRefereeType', '2')
            goals = eT.SubElement(data, 'Goals')
            shots = eT.SubElement(data, 'Shots')
            corners = eT.SubElement(data, 'Corners')
            freek = eT.SubElement(data, 'Freekicks')
            offs = eT.SubElement(data, 'Offsides')
            yell = eT.SubElement(data, 'YellowCards')
            red = eT.SubElement(data, 'RedCards')
            subs = eT.SubElement(data, 'Substitutions')
            pen = eT.SubElement(data, 'Penalties')
            la = eT.SubElement(data, 'LastAction')

            gs = eT.tostring(data, encoding='ISO-8859-1', method='xml')

            with open(match_info['iD'] + "_Gamestats.xml", "wb") as f:
                f.write(gs)

            print(match_info['iD'] + "_Gamestats.xml" + " has been successfully printed.")


def get_match_info(match_folder):
    """
    Search for necessary match information (both team names and matchday) and return them as str.
    :param match_folder:
    :return:
    """
    try:
        gamestats_path = match_folder + r'\Data\Gamestats.xml'
        xml_doc = parse(gamestats_path)
        home_team_element = xml_doc.getElementsByTagName('Team')[0]
        home_team_name = str(dict(home_team_element.attributes.items())['sTeamDesc'])
        away_team_element = xml_doc.getElementsByTagName('Team')[1]
        away_team_name = str(dict(away_team_element.attributes.items())['sTeamDesc'])
        matchday = str(dict(xml_doc.getElementsByTagName('Hego')[0].attributes.items())['iRoundId'])
        comp_id = str(dict(xml_doc.getElementsByTagName('Hego')[0].attributes.items())['iCompetitionId'])

    except FileNotFoundError:
        messagebox.showwarning('MAH Upload',
                               f'The newest folder on C:\\Rec is no MatchID-Folder. Please have a look and '
                               f'restart.')
        sys.exit()

    return home_team_name, away_team_name, matchday, comp_id
