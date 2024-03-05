import sys
from TracabModules.MLS_Teams import MLS
from TracabModules.Internal.gamestats_functions import get_match_info
from TracabModules.Internal.server_manipulations import newest, move_videos
from TracabModules.Internal.scheduleFunctions import get_STSID
import os, shutil


match_folder = newest(r'\\192.168.7.72\Rec')
print(match_folder)
home, away, md, comp = get_match_info(match_folder)
# Define team-dictionary
teams = MLS

# Get 3LCs of both teams
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

# Add both team substrings to get the match string
match = str(ht) + '-' + str(at)
# Get the STS-ID out of the schedule.xml using home and away team names
sts_id, date = get_STSID(comp, home, away)
# create the path of the to-be-created folder for the upload command
filepath_new = os.getcwd() + '\\MD' + str(md) + '_' + match
# Create a folder with the correct naming in the current directory
os.mkdir(filepath_new)
# create the name for the folder as it should be named on the S3 bucket for the upload command
folder_new = str(sts_id) + '_' + match

move_videos(sts_id, match, date, filepath_new)

# Upload folder after all videos have been moved and renamed
if comp == str(1):
    command = ('aws s3 cp "' + filepath_new +
               '" "s3://mah-s3-download-section-mls-331812868623/Video/2024/MLSRegularSeason/Matchweek ' + md + '/'
               + folder_new + '" --recursive')
elif comp == str(100):
    command = ('aws s3 cp "' + filepath_new +
               '" "s3://mah-s3-download-section-mls-331812868623/Video/2024/MLSRehearsals/' + md + '/'
               + folder_new + '" --recursive')

print(command)

try:
    os.system(command)
    input('Upload has finished. Press enter to exit')
    shutil.rmtree(filepath_new)
except:
    input('Upload was not successful. Please try again and submit the error code!')
