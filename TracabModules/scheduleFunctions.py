import ftputil
import pandas as pd
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import gspread
import os


def get_schedule_xml(comp_id, season_id, vendor):
    """

    :param comp_id:
    :param season_id:
    :param vendor:
    :return:
    """

    server = "213.168.127.130"
    user = "Alex_Test"
    password = "RobberyandLahm5%"

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
        ftp_dir = 'D3_MLS/MatchInfo/'
    if vendor == 'keytoq':
        comp_id = '55'
        filename = 'main.xml'
        ftp_dir = 'Keytoq/MatchInfo/'

    # Try statement as workaround due to raised (unknown) error when downloading files from ftp
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


def get_fifa_schedule(filename):
    """
    Parse the schedule.xml of the fifa tournament into a pd.DataFrame that can be pushed to the Google Sheet.
    :param filename:
    :return:
    """

    with open(filename) as fp:
        data = BeautifulSoup(fp, features='html.parser')

    rounds = data.find_all('tournament-round')

    # Create empty DF
    schedule = pd.DataFrame(columns=["Matchday", "MatchID", "KickOff", "Home", "Away", "League", "Stadium"])
    # Get info for all matches and update DF
    for j, round in enumerate(rounds):
        matchday = round["round-key"]
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

            match_info = {"Matchday": matchday, "MatchID": match_id, "KickOff": ko_date, "Home": home, "Away": away,
                          "League": "FIFA Women WC", "Stadium": stadium}

            schedule = schedule.append(pd.DataFrame([match_info]))

    return schedule


def get_d3_schedule(filename):
    """
    Parse the schedule.xml of the deltatre tournament into a pd.DataFrame that can be pushed to the Google Sheet.
    :param filename:
    :return:
    """

    with open(filename) as fp:
        data = BeautifulSoup(fp, 'xml')

    # Get division
    league = data.find_all("sports-content-code")[1]["code-name"]
    # division = data.find("tournament-division-metadata")["division-key"]
    # league = division + "." + league_name

    # Get all matchdays
    rounds = data.find_all("tournament-round")

    # Create a DF containing all matches of a complete season
    schedule = pd.DataFrame(columns=["Matchday", "MatchID", "KickOff", "Home", "Away", "League", "Stadium"])
    # Iterate the whole season
    for i, round in enumerate(rounds):
        round_id = i + 1
        matchday = []
        # Get match specific information
        for j, match in enumerate(round.contents[1::2]):
            matchId = match.contents[1]["event-key"]
            home = match.contents[3].contents[1].contents[1]["full"].encode("latin").decode("utf-8")
            away = match.contents[5].contents[1].contents[1]["full"].encode("latin").decode("utf-8")
            stadium = match.contents[1].contents[1].contents[1].contents[1]["full"].encode("latin").decode("utf-8")
            date = match.contents[1]["start-date-time"][0:4] + "-" \
                   + match.contents[1]["start-date-time"][4:6] + "-" \
                   + match.contents[1]["start-date-time"][6:8]
            ko = match.contents[1]["start-date-time"][9:11] + ":" \
                 + match.contents[1]["start-date-time"][11:13]
            ko_date = date + " " + ko
            match_info = {"Matchday": round_id, "MatchID": matchId, "KickOff": ko_date, "Home": home, "Away": away,
                          "League": league, "Stadium": stadium}
            matchday.append(match_info)
        md_df = pd.DataFrame(matchday)
        schedule = pd.concat([schedule, md_df])

    return schedule


def get_d3_mls_schedule(filename):
    """
    Parse the schedule.xml of the mls tournament into a pd.DataFrame that can be pushed to the Google Sheet.
    :param filename:
    :return:
    """

    with open(filename) as fp:
        data = BeautifulSoup(fp, 'xml')

    # Get all matches
    fixtures = data.find_all("Fixture")
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
        matchday = match["MatchDay"]
        stadium = match["StadiumName"].encode("latin").decode("utf-8")

        match_info = {"Matchday": matchday, "MatchID": match_id, "KickOff": kickoff, "Home": home, "Away": away,
                      "League": league, "Stadium": stadium}

        schedule = schedule.append(pd.DataFrame([match_info]))

    return schedule


def get_opta_schedule(schedule_filename, squad_filename):
    """
    Parse the schedule.xml of the opta tournament into a pd.DataFrame that can be pushed to the Google Sheet.
    :param schedule_filename:
    :param squad_filename:
    :return:

    """

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
    md = [x.find('MatchInfo')['MatchDay'] for x in matches]
    match_ids = [x['uID'][1:] for x in matches]
    dates = [x.find('MatchInfo').find('Date').text for x in matches]
    stadiums = [x.find('Stat').text for x in matches]
    home_teams = [team_dict[x.find_all('TeamData')[0]['TeamRef']] for x in matches]
    away_teams = [team_dict[x.find_all('TeamData')[1]['TeamRef']] for x in matches]
    league = ['Eredivisie' for i in range(0, 306)]

    schedule = pd.DataFrame(list(zip(md, match_ids, dates, home_teams, away_teams, league, stadiums)))

    return schedule


def get_keytoq_schedule(filename):
    """
    Parse the schedule.xml of the Ekstraklasa into a pd.DataFrame that can be pushed to the Google Sheet.
    :param filename:
    :return:
    """

    with open(filename,
              encoding='utf8') as fp:
        schedule_data = BeautifulSoup(fp, 'xml')

    matches = [x.find_all('match') for x in schedule_data.find_all('round').content()]

    schedule = pd.DataFrame(columns=["Matchday", "MatchID", "KickOff", "Home", "Away", "League", "Stadium"])
    for i, md in enumerate(matches):
        ko_date = [x['date'] + '' + x['time'] for x in md]
        home = [x['team_a'] for x in md]
        away = [x['team_b'] for x in md]
        matchId = [x['id'] for x in md]
        league = ['Ekstraklasa' for x in md]
        round_id = [str((i + 1)) for x in md]

        match_info = pd.DataFrame(
            {"Matchday": round_id, "MatchID": matchId, "KickOff": ko_date, "Home": home, "Away": away,
             "League": league})
        schedule = pd.concat([schedule, match_info])

    return schedule


def push_to_google(schedule, league):
    """

    :param schedule:
    :param league:
    :return:
    """

    os.chdir("N:\\07_QC\\Scripts\\Schedule_script\\Season23-24")
    gc = gspread.oauth(credentials_filename=
                       '../Matchfacts-3dfad71ae74c.json'
                       )

    schedule_sheet = gc.open_by_key("14Dx1un2S9USaZX_5OyL2JALvxW4Fg18_OzJXaSuwYmc")
    if schedule_sheet.worksheet(league) is False:
        worksheet = schedule_sheet.add_worksheet(title=league, rows=1000, cols=20)
    else:
        worksheet = schedule_sheet.worksheet(league)
    worksheet.update([schedule.columns.values.tolist()] + schedule.values.tolist())

    return print('The schedule of ' + league + ' has been successfully pushed to the Google Sheet "23/24 Schedule"')