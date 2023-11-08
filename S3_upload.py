"""
Automize the upload of video feeds to the S3 database

1.) What file should be uploaded?
    - Take filepath as input
2.) Create cmd command
    - Paste input into line
    - Adjust upload-location / file name accordingly
3.) Execute cmd command and upload files
"""
from TracabModules.s3_functions import get_STSID
import glob, os, shutil

# Create a team dict to have 3LCs for all MLS teams available and map them with their full name
# Currently only PlayOff teams!
teams = {'NYRB': 'New York Red Bulls', 'CLT': 'Charlotte FC', 'SKC': 'Sporting Kansas City',
         'SJ': 'San Jose Earthquakes',
         'ORL': 'Orlando City', 'CIN': 'FC Cincinnati', 'NSH': 'Nashville SC', 'CLB': 'Columbus Crew',
         'ATL': 'Atlanta United', 'PHI': 'Philadelphia Union', 'NE': 'New England Revolution',
         'STL': 'St. Louis CITY SC',
         'SEA': 'Seattle Sounders FC', 'DAL': 'FC Dallas', 'LAFC': 'Los Angeles Football Club',
         'VAN': 'Vancouver Whitecaps FC',
         'HOU': 'Houston Dynamo FC', 'RSL': 'Real Salt Lake'}

# Create dictionary for video feeds
feeds = {'1': 'TacticalFeed.mp4', '2': 'PanoramicFeed.mp4', '3': 'HighBehind_2.mp4', '4': 'HighBehind_1.mp4'}

# Request user input on home and away team and matchday
# Implemented a safety to only accept existing 3LCs and the correct matchday format
while True:
    ht = input(' \n Please insert the three letter code of your home team \n')
    try:
        home_team = teams[ht]
    except:
        # input was incorrect
        print('Invalid three letter code')
        continue
    else:
        # input was correct
        break
while True:
    at = input(' \n Please insert the three letter code of your away team \n')
    try:
        away_team = teams[at]
    except:
        print('Invalid three letter code')
        continue
    else:
        break

while True:
    md = str(input(' \n Please insert the matchday \n'))
    if int(md) < 10 and len(md) == 1:
        break
    elif int(md) >= 10 and len(md) == 2:
        break
    else:
        print(' \n Wrong format. E.g., try 1 instead of 01.')
        continue


# Add both team substrings to get the match string
match = ht + '-' + at
# Get the STS-ID out of the schedule.xml using home and away team names
sts_id, date = get_STSID(2, home_team, away_team)
#sts_id = 'MLS-MAT-000168'
# filepath_new = os.getcwd()
# Create a folder with the correct naming on the desktop
os.mkdir(os.getcwd() + '\\MD' + md + '_' + match)
# save the new path of the created folder for the upload command
filepath_new = os.getcwd() + '\\MD' + md + '_' + match
# save the name of the new folder as a name for the upload command
folder_new = '/MD' + md + '_' + match

# Loop, that goes through all four feeds to move and rename them
for feed, i in enumerate(feeds):
    print(feeds[i])
    filename_new = sts_id + '_' + match + '_' + feeds[i]
    # open folder of specific isma server to rename video feed
    # os.chdir("C:\\Users\\alexa\\Desktop\\MD34_NYCvMIA")
    # yesterday = (date.today()- timedelta(days=1)).strftime('%Y_%m_%d')
    # today = date.today().strftime('%Y_%m_%d')
    if feeds[i] == 'TacticalFeed.mp4':
        os.chdir(r'\\192.168.7.75\d\CastRouterVideoAndSetupXML' + '\\' + date)
        for file in glob.glob("*.mp4"):
            print(filepath_new + '\\' + filename_new)
            shutil.move(file, filepath_new + '\\' + filename_new)
    elif feeds[i] == 'PanoramicFeed.mp4':
        os.chdir(r'\\192.168.7.74\d\CastRouterVideoAndSetupXML' + '\\' + date)
        for file in glob.glob("*.mp4"):
            print(filepath_new + '\\' + filename_new)
            shutil.move(file, filepath_new + '\\' + filename_new)
    elif feeds[i] == 'HighBehind_1.mp4' or feeds[i] == 'HighBehind_2.mp4':
        os.chdir(r'\\192.168.7.76\d\CastRouterVideoAndSetupXML' + '\\' + date)
        for file in glob.glob("*.mp4"):
            if feeds[i] == 'HighBehind_2.mp4' and 'PanoB' in file:
                print(filepath_new + '\\' + filename_new)
                shutil.move(file, filepath_new + '\\' + filename_new)
            elif feeds[i] == 'HighBehind_1.mp4' and 'PanoD' in file:
                print(filepath_new + '\\' + filename_new)
                shutil.move(file, filepath_new + '\\' + filename_new)

print('All files have been moved and renamed')

# Upload folder after all videos have been moved and renamed
command = 'aws s3 cp "' + filepath_new + '" "s3://mah-s3-download-section-mls-331812868623/Video/2023/MLSCupPlayoffs' \
          + folder_new + '" --recursive'

print(command)

try:
    os.system(command)
    input('Upload has finished. Press enter to exit')
except:
    input('Upload was not successful. Please try again and submit the error code!')

