"""
Purpose of this code is to find the latest HTF videos that were just rendered into .mp4 and then rename them according
STS requirements.

v1.0: 2024/03/08 11:45
    - First version already able to rename the videos accordingly
    - Currently this version needs to be adjusted based on bl1 or bl2 usage
    - SuperCup for BL1 schedule is neglected. NEEDS TO BE ADJUSTED FOR UPCOMING SEASON!!!
v1.1: 2024/03/08 14:20
    - Added additional check for the existence of both or only one HTF
v1.2: 2024/03/12 13:35
    - Added some GUI at the end indicating when files have been renamed
    - Added some logging information
    - Added additional functions and modularity
"""
import pandas as pd
import logging
from TracabModules.Internal.server_manipulations import choose_file, display_popup, rename_htf_files

# Constants
DEFAULT_PATH_HTF1 = r'D:\B'
DEFAULT_PATH_HTF2 = r'E:\D'
BL1_SCHEDULE_PATH = r'C:\Users\tracab\Desktop\BL1_HTF_Schedule.xlsx'
ALLOWED_FILE_TYPES = ("MP4 files", "*.mp4")

# Add this at the beginning of your script
logging.basicConfig(level=logging.INFO)

latest_htf1 = choose_file(DEFAULT_PATH_HTF1, feed="HTF_1", allowed_types=("MP4 files", "*.mp4"))
latest_htf2 = choose_file(DEFAULT_PATH_HTF2, feed="HTF_2", allowed_types=("MP4 files", "*.mp4"))

match = latest_htf1[-13:-6].replace('_', '-')

bl1_schedule = pd.read_excel(r'C:\Users\tracab\Desktop\BL1_HTF_Schedule.xlsx', header=1)

# Right/Left is seen from the benches => Default: left == HTF2
new_htf2 = bl1_schedule.loc[bl1_schedule['3LC'] == match]['High Behind Left'].values[0]
new_htf1 = bl1_schedule.loc[bl1_schedule['3LC'] == match]['High Behind Right'].values[0]

# Rename the available HTFs
rename_htf_files(latest_htf2, DEFAULT_PATH_HTF2, new_htf2)
rename_htf_files(latest_htf1, DEFAULT_PATH_HTF1, new_htf1)

# Display popup window with information
display_popup("Renaming HTFs", "Files have bee successfully renamed!")
