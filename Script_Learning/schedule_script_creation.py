from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta


with open('C:\\Users\\alexa\\PycharmProjects\\Work_Tracab\\Script_Learning\\schedule.xml') as fp:
    data = BeautifulSoup(fp, 'xml')


# Get division
league_name = data.find_all("sports-content-code")[1]["code-name"]
division = data.find("tournament-division-metadata")["division-key"]
league = division + "." + league_name
# Get all matchdays
rounds = data.find_all("tournament-round")

# Get round_id
round_id = rounds[0]["round-number"]

# Get all matches from a matchday
sports_event = rounds[0].contents[1::2]

# Get matchID
matchId = sports_event[0].contents[1]["event-key"]

# Get hometeam
home = sports_event[0].contents[3].contents[1].contents[1]["full"].encode("latin").decode("utf-8")

# Get awayteam
away = sports_event[0].contents[5].contents[1].contents[1]["full"].encode("latin").decode("utf-8")

# Get stadium
stadium = sports_event[0].contents[1].contents[1].contents[1].contents[1]["full"].encode("latin").decode("utf-8")

# Get date and KO time
# year = sports_event[0].contents[1]["start-date-time"][0:4]
# month = sports_event[0].contents[1]["start-date-time"][4:6]
# day = sports_event[0].contents[1]["start-date-time"][6:8]

date = sports_event[0].contents[1]["start-date-time"][0:4] + "-" + sports_event[0].contents[1]["start-date-time"][4:6] \
       + "-" + sports_event[0].contents[1]["start-date-time"][6:8]

# h = sports_event[0].contents[1]["start-date-time"][-11:-9]
# min = sports_event[0].contents[1]["start-date-time"][-9:-7]

ko = sports_event[0].contents[1]["start-date-time"][-11:-9] + ":" \
         + sports_event[0].contents[1]["start-date-time"][-9:-7]

KO_date = date + " " + ko

match = {"Matchday": round_id, "MatchID": matchId, "KickOff": KO_date, "Home": home, "Away": away,
         "League": league, "Stadium": stadium}



# Get division
league_name = data.find_all("sports-content-code")[1]["code-name"]
division = data.find("tournament-division-metadata")["division-key"]
league = division + "." + league_name

# Get all matchdays
rounds = data.find_all("tournament-round")

# Create a DF containing all matches of a complete season
season = pd.DataFrame(columns=["Matchday", "MatchID", "KickOff", "Home", "Away", "League", "Stadium"])
# Iterate the whole season
for i, round in enumerate(rounds):
    round_id = i+1
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
        date = match.contents[1]["start-date-time"][0:4] + "-" \
               + match.contents[1]["start-date-time"][4:6] + "-" \
               + match.contents[1]["start-date-time"][6:8]
        KO_date = date + " " + ko
        match_info = {"Matchday": round_id, "MatchID": matchId, "KickOff": KO_date, "Home": home, "Away": away,
                      "League": league, "Stadium": stadium}
        matchday.append(match_info)
    md_df = pd.DataFrame(matchday)
    season = season.append(md_df)




#### Testing

time_change = datetime.strptime('2023-03-26 02:00', '%Y-%m-%d %H:%M')
new_date = datetime.strptime(KO_date, '%Y-%m-%d %H:%M')
new_date = new_date + timedelta(hours=2)

new_date < time_change