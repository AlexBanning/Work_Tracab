"""
Automize the upload of video feeds to the S3 database

v2.0 2024/03/14 09:40
    - Improved modularity for future adjustments
    - Renamed to MAH_upload.py to lose redundant and long name
    - Added parameters to enable easy implementations of special set-ups if file-locations differ from default

"""
import shutil
import sys
# from MLS.MLS_Teams import MLS, LeaguesCup, OpenCup, AllStar
from TracabModules.Internal.gamestats_functions import get_match_info
from TracabModules.Internal.server_manipulations import newest_folder, move_and_rename_feed
from TracabModules.Internal.scheduleFunctions import get_STSID
import os

import json

exe_dir = getattr(sys, '_MEIPASS', os.getcwd())
with open(os.path.join(exe_dir,'mls_teams_config_test.json'), 'r',
          encoding='utf-8') as file:
    config = json.load(file)


match_folder = newest_folder(r'\\192.168.7.72\Rec')
# newest(r'\\192.168.7.72\Rec ')
print(f'Matchfolder: {match_folder} \n')
home, away, md, comp, match_id = get_match_info(match_folder)

teams = config['teams'][comp]
# Define team-dictionary
# if comp == '1':
#     teams = MLS
# elif comp == '6':
#     teams = LeaguesCup
# elif comp == '102':
#     teams = OpenCup
# elif comp == '5':
#     teams = AllStar

# Get 3LCs of both teams
try:
    ht = teams[home]
except KeyError:
    # print('Home team is not in the teams-dictionary. Please check with the Developer!')
    input('The home team cannot be found in the database. Please check with the developer.\n'
          'Please Insert the 3LC and Team Name!')
    ht = str(input())
    home = str(input())
    sys.exit()

try:
    at = teams[away]
except KeyError:
    input('The away team cannot be found in the database. Please check with the developer.\n'
          'Press Enter to leave!')
    at = str(input())
    away = str(input())
    sys.exit()

# Add both team substrings to get the match string
match = str(ht) + '-' + str(at)
# Get the STS-ID out of the schedule.xml using home and away team names
sts_id, date = get_STSID(comp, match_id, season_id='8', season_dir='Season24-25')
# create the path of the to-be-created folder for the upload command
filepath_new = fr'{os.getcwd()}\MD{str(md)}_{match}_{comp}'
# Create a folder with the correct naming in the current directory
try:
    os.mkdir(filepath_new)
except FileExistsError:
    shutil.rmtree(filepath_new)
    os.mkdir(filepath_new)
# create the name for the folder as it should be named on the S3 bucket for the upload command
folder_new = f'{str(sts_id)}_{match}'

move_and_rename_feed(filepath_new=filepath_new, sts_id=sts_id, match=match, date=date)

# Upload folder after all videos have been moved and renamed
formatted_command = config['commands'][comp].format(filepath_new=filepath_new, md=md, folder_new=folder_new)
# Command still f-string, not in correct format for aws command

competition = config['competitions'][comp]
command = (fr'aws s3 cp {filepath_new} s3://mah-s3-download-section-mls-331812868623/Video/2024/'
           fr'{competition}/{md}/{folder_new} --recursive')

print(f'\nExecuting S3 Command: {formatted_command}\n')
try:
    os.system(command)
    input('Upload has finished. Press enter to exit')
except:
    input('Upload was not successful. Please try again and submit the error code!')
