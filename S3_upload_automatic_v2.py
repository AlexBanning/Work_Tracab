"""
Automize the upload of video feeds to the S3 database

1.) What file should be uploaded?
    - Take filepath as input
2.) Create cmd command
    - Paste input into line
    - Adjust upload-location / file name accordingly
3.) Execute cmd command and upload files
"""
import glob
import os
import shutil
import sys
from TracabModules.MLS_Teams import MLS
from TracabModules.s3_functions import get_STSID, newest, get_match_info
import glob, os, shutil

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
match = str(ht) + 'vs' + str(at)
# Get the STS-ID out of the schedule.xml using home and away team names
sts_id, date = get_STSID(comp, home, away)
# create the path of the to-be-created folder for the upload command
filepath_new = os.getcwd() + '\\MD' + str(md) + '_' + match
# Create a folder with the correct naming in the current directory
os.mkdir(filepath_new)
# create the name for the folder as it should be named on the S3 bucket for the upload command
folder_new = str(sts_id) + '_' + match

# Create dictionary for video feeds
feeds = {'1': 'TacticalFeed.mp4', '2': 'PanoramicFeed.mp4', '4': 'HighBehind_2.mp4',
         '5': 'HighBehind_1.mp4'}

# Loop, that goes through all four feeds to move and rename them
for feed, i in enumerate(feeds):
    print(feeds[i])
    filename_new = sts_id + '_' + match + '_' + feeds[i]
    # open folder of specific isma server to rename video feed
    # os.chdir("C:\\Users\\alexa\\Desktop\\MD34_NYCvMIA")
    # yesterday = (date.today()- timedelta(days=1)).strftime('%Y_%m_%d')
    # today = date.today().strftime('%Y_%m_%d')
    if feeds[i] == 'TacticalFeed.mp4':
        os.chdir(r'\\192.168.7.75\d\TraCamVideoAndSetupXML' + '\\' + date)
        for file in glob.glob("*.mp4"):
            print(filepath_new + '\\' + filename_new)
            shutil.move(file, filepath_new + '\\' + filename_new)
    if feeds[i] == 'PanoramicFeed.mp4':
        os.chdir(r'\\192.168.7.74\d\TraCamVideoAndSetupXML' + '\\' + date)
        for file in glob.glob("*.mp4"):
            print(filepath_new + '\\' + filename_new)
            shutil.move(file, filepath_new + '\\' + filename_new)
    elif feeds[i] == 'HighBehind_1.mp4' or feeds[i] == 'HighBehind_2.mp4':
        os.chdir(r'\\192.168.7.76\d\TraCamVideoAndSetupXML' + '\\' + date)
        for file in glob.glob("*.mp4"):
            if feeds[i] == 'HighBehind_2.mp4' and 'PanoB' in file:
                print(filepath_new + '\\' + filename_new)
                shutil.move(file, filepath_new + '\\' + filename_new)
            elif feeds[i] == 'HighBehind_1.mp4' and 'PanoD' in file:
                print(filepath_new + '\\' + filename_new)
                shutil.move(file, filepath_new + '\\' + filename_new)

print('All files have been moved and renamed')

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
    shutil.rmtree(filepath_new)
    input('Upload has finished. Press enter to exit')
except:
    input('Upload was not successful. Please try again and submit the error code!')
