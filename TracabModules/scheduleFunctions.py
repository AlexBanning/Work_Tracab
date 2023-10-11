import ftputil
import pandas as pd
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import gspread
import os
import xml.etree.ElementTree as ET


def get_schedule_xml(comp_id, vendor, **kwargs):
    """
    Download all required xml-files for the schedule of specified competition
    :param comp_id:
    :param vendor:
    :param vendor:

    """

    server = "213.168.127.130"
    user = "Alex_Test"
    password = "RobberyandLahm5%"
    season_id = kwargs.get("season_id", None)

    if vendor == 'deltatre':
        filename = 'schedule.xml'
        ftp_dir = 'deltatre/MatchInfo/' + str(comp_id) + '/' + str(season_id) + '/schedule'
    if vendor == 'FIFA':
        filename = str(comp_id) + '_schedule.xml'
        ftp_dir = 'FIFA/' + str(comp_id) + '/'
    if vendor == 'opta':
        schedule_filename = 'srml-' + str(comp_id) + '-' + str(season_id) + '-results.xml'
        squads_filename = 'srml-' + str(comp_id) + '-' + str(season_id) + '-squads.xml'
        ftp_dir = 'Opta/MatchInfo'
    if vendor == 'd3_mls':
        filename = 'Feed_01_06_basedata_fixtures_MLS-COM-00000' + str(comp_id) + '.xml'
        # correct file: 'Feed_01_06_basedata_fixtures_MLS-SEA-0001K7_MLS-COM-000001.xml'
        ftp_dir = 'D3_MLS/MatchInfo/'
    if vendor == 'keytoq':
        comp_id = '55'
        filename = 'main.xml'
        ftp_dir = 'Keytoq/MatchInfo/'

    # Try statement as workaround due to raised (unknown) error when downloading files from ftp
    # Change directory so the schedules are downloaded into the MatchInfo folder
    os.chdir("N:\\07_QC\\Scripts\\Schedule_script\\Season23-24\\MatchInfo")
    try:
        if vendor != 'opta':
            with ftputil.FTPHost(server, user, password) as ftp_host:
                ftp_host.chdir(ftp_dir)
                ftp_host.open(filename)
                if ftp_host.path.isfile(filename):
                    ftp_host.download(filename, filename)
    except:
        pass
    try:
        if vendor == 'opta':
            with ftputil.FTPHost(server, user, password) as ftp_host:
                ftp_host.chdir(ftp_dir)
                ftp_host.open(schedule_filename)
                if ftp_host.path.isfile(schedule_filename):
                    ftp_host.download(schedule_filename, schedule_filename)
                ftp_host.open(squads_filename)
                if ftp_host.path.isfile(squads_filename):
                    ftp_host.download(squads_filename, squads_filename)
    except:
        pass

    return print('The schedule for competition ' + str(comp_id) + ' of ' + str(vendor) + ' has been downloaded')


def get_fifa_schedule(comp_id, filename):
    """
    Parse the schedule.xml of the fifa tournament into a pd.DataFrame that can be pushed to the Google Sheet.
    :param comp_id:
    :param filename:
    :return:
        schedule: pd.df
        Dataframe containing the whole available schedule for the competition
    """

    global league
    os.chdir("N:\\07_QC\\Scripts\\Schedule_script\\Season23-24\\MatchInfo")
    with open(filename) as fp:
        data = BeautifulSoup(fp, features='html.parser')

    rounds = data.find_all('tournament-round')

    # Create empty DF
    schedule = pd.DataFrame(columns=["Matchday", "MatchID", "KickOff", "Home", "Away", "League", "Stadium"])
    # Get info for all matches and update DF
    for j, round in enumerate(rounds):
        matchday = int(round["round-key"])
        fixtures = round.find_all("sports-event")
        for i, match in enumerate(fixtures):
            date = match.find("event-metadata")["start-date-time"][0:10]
            time = match.find("event-metadata")["start-date-time"][11:16]
            ko_date = (datetime.strptime(date + ' ' + time, "%Y-%m-%d %H:%M") + timedelta(hours=2)
                       ).strftime("%Y-%m-%d %H:%M")
            home = match.find_all("team")[0].find("team-metadata").find("name")["full"].encode("latin").decode("utf-8")
            away = match.find_all("team")[1].find("team-metadata").find("name")["full"].encode("latin").decode("utf-8")
            match_id = match.find("event-metadata")["event-key"]
            stadium = match.find("event-metadata").find("site").find("site-metadata").find("name")["full"].encode(
                "latin").decode("utf-8")
            # Check which competition to add the accurate league. Info is missing in schedule.xml
            if comp_id == '285026':
                league = 'FIFA Women WC'

            match_info = pd.DataFrame(
                {"Matchday": matchday, "MatchID": match_id, "KickOff": ko_date, "Home": home, "Away": away,
                 "League": league, "Stadium": stadium}, index=[0])

            schedule = pd.concat([schedule, match_info])

    return schedule


def get_d3_schedule(comp_id, filename):
    """
    Parse the schedule.xml of the deltatre tournament into a pd.DataFrame that can be pushed to the Google Sheet.
    :param comp_id:
    :param filename:
    :return:
        schedule: pd.df
        Dataframe containing the whole available schedule for the competition
    """

    # Parse in the schedule
    tree = ET.parse("N:\\07_QC\\Scripts\\Schedule_script\\Season23-24\\MatchInfo\\" + filename)
    root = tree.getroot()
    # Get (if available) both halfs (all rounds) of a tournament, e.g. 'Hinrunde', 'Rückrunde'
    division = [x for x in root[1][1:]]

    # Empty dataframe where each matchday can get added to
    schedule = pd.DataFrame(columns=["Matchday", "MatchID", "KickOff", "Home", "Away", "League", "Stadium"])

    # first level of loop iterating through all 'runden' of the tournament
    for div in division:
        mds = [x for x in div[1:]]  # all match-days of the round (e.g., 17 in BL1 and BL2)

        # second level of loop iterating through list containing all match-days
        for md in mds:
            tournament = root[1][1][1]
            if comp_id != 51:
                league = [root[0][1][1].attrib['code-name'].replace(' ', '') for x in md]
            else:
                league = ['1.Bundesliga' for x in md]
            round_id = [int(md.attrib['round-number']) for x in md]
            home_teams = [x[1][0][0].attrib['full'] for x in md]
            away_teams = [x[2][0][0].attrib['full'] for x in md]
            match_ids = [x[0].attrib['event-key'] for x in md]
            dates = [x[0].attrib['start-date-time'][0:4] + '-' +
                     y[0].attrib['start-date-time'][4:6] + '-' +
                     z[0].attrib['start-date-time'][6:8] + ' ' +
                     h[0].attrib['start-date-time'][9:11] + ':' +
                     m[0].attrib['start-date-time'][11:13]
                     for x, y, z, h, m in zip(md, md, md, md, md)]
            stadiums = [x[0][0][0][0].attrib['full'] for x in md]

            matchday = pd.DataFrame(list(zip(round_id, match_ids, dates, home_teams, away_teams, league, stadiums)),
                                    columns=['Matchday', 'MatchID', 'KickOff', 'Home', 'Away', 'League', 'Stadium'])

            schedule = pd.concat([schedule, matchday])

    return schedule


def get_d3_mls_schedule(filename):
    """
    Parse the schedule.xml of the mls tournament into a pd.DataFrame that can be pushed to the Google Sheet.
    :param filename:
    :return:
        schedule: pd.df
        Dataframe containing the whole available schedule for the competition
    """

    os.chdir("N:\\07_QC\\Scripts\\Schedule_script\\Season23-24\\MatchInfo")
    with open(filename) as fp:
        data = BeautifulSoup(fp, 'xml')

    # Get all matches
    fixtures = data.find_all("Fixture")
    # Current workaround as long as older seasons are also implemented in the schedule.xml
    fixtures = [x for x in fixtures if x['Season'] == '2023/2024']
    # Define TimeSaving-Dates
    dst_start = datetime.strptime('2023-03-26 02:00', '%Y-%m-%d %H:%M')
    dst_end = datetime.strptime('2023-10-29 03:00', '%Y-%m-%d %H:%M')
    # Define league
    league = 'MLS'
    # Create empty DF
    schedule = pd.DataFrame(columns=["Matchday", "MatchID", "KickOff", "Home", "Away", "League", "Stadium"])
    # Get info for all matches and update DF
    for i, match in enumerate(fixtures):
        date = match["PlannedKickoffTime"][0:10]
        time = match["PlannedKickoffTime"][11:16]
        kickoff = date + ' ' + time
        ko_date_object = datetime.strptime(kickoff, '%Y-%m-%d %H:%M')
        if dst_start < ko_date_object < dst_end:
            ko_date_object = ko_date_object + timedelta(hours=2)
        else:
            ko_date_object = ko_date_object + timedelta(hours=1)
        kickoff = ko_date_object.strftime('%Y-%m-%d %H:%M')
        home = match["HomeTeamName"].encode("latin").decode("utf-8")
        away = match["GuestTeamName"].encode("latin").decode("utf-8")
        match_id = match["DlProviderId"]
        matchday = int(match["MatchDay"])
        stadium = match["StadiumName"].encode("latin").decode("utf-8")

        match_info = pd.DataFrame(
            {"Matchday": matchday, "MatchID": match_id, "KickOff": kickoff, "Home": home, "Away": away,
             "League": league, "Stadium": stadium}, index=[0])

        schedule = pd.concat([schedule, match_info])

    return schedule


def get_opta_schedule(comp_id, schedule_filename, squad_filename):
    """
    Parse the schedule.xml of the opta tournament into a pd.DataFrame that can be pushed to the Google Sheet.
    :param comp_id: Int
        Individual ID of the competition
    :param schedule_filename: Str
        Name of the schedule.xml for the competition
    :param squad_filename: Str
        Name of the squad.xml for the competition
    :return:
        schedule: pd.df
        Dataframe containing the whole available schedule for the competition

    """

    os.chdir("N:\\07_QC\\Scripts\\Schedule_script\\Season23-24\\MatchInfo")
    with open(schedule_filename,
              encoding='utf8') as fp:
        schedule_data = BeautifulSoup(fp, 'xml')

    # Open team info
    with open(squad_filename,
              encoding='utf8') as fp:
        team_data = BeautifulSoup(fp, 'xml')

    # Create dictionary to link team_name and team_id
    teams = team_data.find_all('Team')
    team_names = [x.find('Name').text for x in teams]
    team_ids = [x['uID'] for x in teams]
    team_dict = dict(zip(team_ids, team_names))

    # Create schedule
    matches = schedule_data.find_all('MatchData')
    md = [int(x.find('MatchInfo')['MatchDay']) for x in matches]
    match_ids = [x['uID'][1:] for x in matches]
    # dates = [x.find('MatchInfo').find('Date').text[:-3] for x in matches]
    dates = [datetime.strftime(datetime.strptime(x.find('MatchInfo').find('Date').text[:-3], '%Y-%m-%d %H:%M') +
                               timedelta(hours=1), '%Y-%m-%d %H:%M') for x in matches]
    stadiums = [x.find('Stat').text for x in matches]
    home_teams = [team_dict[x.find_all('TeamData')[0]['TeamRef']] for x in matches]
    away_teams = [team_dict[x.find_all('TeamData')[1]['TeamRef']] for x in matches]
    if int(comp_id) == 9:
        league = ['Eredivisie' for i in range(0, 306)]
    elif int(comp_id) == 5:
        league = ['CL' for i in range(0, 306)]
    if int(comp_id) == 6:
        league = ['EL' for i in range(0, 306)]

    schedule = pd.DataFrame(list(zip(md, match_ids, dates, home_teams, away_teams, league, stadiums)),
                            columns=['Matchday', 'MatchID', 'KickOff', 'Home', 'Away', 'League', 'Stadium'])

    return schedule


def get_keytoq_schedule(filename):
    """
    Parse the schedule.xml of the Ekstraklasa into a pd.DataFrame that can be pushed to the Google Sheet.
    :param filename:
    :return:
    """

    os.chdir("N:\\07_QC\\Scripts\\Schedule_script\\Season23-24\\MatchInfo")
    with open(filename,
              encoding='utf8') as fp:
        schedule_data = BeautifulSoup(fp, 'xml')

    matches = [x.find_all('match') for x in schedule_data.find_all('round')]

    schedule = pd.DataFrame(columns=["Matchday", "MatchID", "KickOff", "Home", "Away", "League"])
    for i, md in enumerate(matches):
        ko_date = [x['date'] + ' ' + x['time'] for x in md]
        home = [x['team_a'] for x in md]
        away = [x['team_b'] for x in md]
        matchId = [x['id'] for x in md]
        league = ['Ekstraklasa' for x in md]
        round_id = [(i + 1) for x in md]

        match_info = pd.DataFrame(
            {"Matchday": round_id, "MatchID": matchId, "KickOff": ko_date, "Home": home, "Away": away,
             "League": league})
        schedule = pd.concat([schedule, match_info])

    return schedule


def push_to_google(schedule, league):
    """
    Takes in a pd.DataFrame and pushes it into the Google Sheet '23/24 Schedule'.
    :param schedule: pd.DataFrame
        pd.DataFrame that contains the relevant schedule
    :param league: str
        Name of the league and therefore of the worksheet that needs to be updated
    :return:
    """

    os.chdir("N:\\07_QC\\Scripts\\Schedule_script\\Season23-24")
    gc = gspread.oauth(credentials_filename=
                       'schedule_push_authentification.json'
                       )

    schedule_sheet = gc.open_by_key("14Dx1un2S9USaZX_5OyL2JALvxW4Fg18_OzJXaSuwYmc")
    try:
        worksheet = schedule_sheet.worksheet(league)
    except gspread.WorksheetNotFound:
        schedule_sheet.add_worksheet(title=league, rows=1000, cols=15)
    worksheet = schedule_sheet.worksheet(league)
    worksheet.update([schedule.columns.values.tolist()] + schedule.values.tolist())

    return print('The schedule of ' + league + ' has been successfully pushed to the Google Sheet "23/24 Schedule"')
