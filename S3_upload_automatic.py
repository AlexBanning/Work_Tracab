"""
Automize the upload of video feeds to the S3 database

1.) What file should be uploaded?
    - Take filepath as input
2.) Create cmd command
    - Paste input into line
    - Adjust upload-location / file name accordingly
3.) Execute cmd command and upload files
"""
from TracabModules.s3_functions import get_STSID, newest, get_match_info
import glob, os, shutil, sys


match_folder = newest(r'\\192.168.7.72\Rec')
print(match_folder)
home, away, md = get_match_info(match_folder)


# Create a team dict to have 3LCs for all MLS teams available and map them with their full name
# Currently only PlayOff teams!
teams = {'New York Red Bulls': 'NYRB', 'Charlotte FC': 'CLT', 'Sporting Kansas City': 'SKC',
         'San Jose Earthquakes': 'SJ',
         'Orlando City': 'ORL', 'FC Cincinnati': 'CIN', 'Nashville SC': 'NSH', 'Columbus Crew': 'CLB',
         'Atlanta United': 'ATL', 'Philadelphia Union': 'PHI', 'New England Revolution': 'NE',
         'St. Louis CITY SC': 'STL',
         'Seattle Sounders FC': 'SEA', 'FC Dallas': 'DAL', 'Los Angeles Football Club': 'LAFC',
         'Vancouver Whitecaps FC': 'VAN',
         'Houston Dynamo FC': 'HOU', 'Real Salt Lake': 'RSL', 'Inter Miami CF': 'MIA', 'New York City FC': 'NYC',
         'LA Galaxy': 'LA', 'D.C. United': 'DC', 'CF Montréal': 'MTL', 'Toronto FC': 'TOR', 'Chicago Fire FC': 'CHI',
         'Minnesota United': 'MIN', 'Austin FC': 'ATX', 'Colorado Rapids': 'COL', 'Portland Timbers': 'POR' }


try:
    ht = teams[home]
except KeyError:
    # print('Home team is not in the teams-dictionary. Please check with the Developer!')
    input('The home team cannot be found in the database. Please check with the developer.\n'
          'Press Enter to leave!')
    sys.exit()

try:
    at = teams[away]
except KeyError:
    input('The away team cannot be found in the database. Please check with the developer.\n'
          'Press Enter to leave!')
    sys.exit()
    
# Create dictionary for video feeds
feeds = {'1': 'TacticalFeed.mp4', '2': 'PanoramicFeed.mp4', '3': 'HighBehind_2.mp4', '4': 'HighBehind_1.mp4'}

# Add both team substrings to get the match string
match = ht + '-' + at
# Get the STS-ID out of the schedule.xml using home and away team names
sts_id, date = get_STSID(2, home, away)
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

