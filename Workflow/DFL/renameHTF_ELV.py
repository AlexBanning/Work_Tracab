"""
Purpose of this code is to find the latest HTF videos that were just rendered into .mp4 and then rename them according
STS requirements.
"""
import pandas as pd
import logging
from TracabModules.Internal.server_manipulations import choose_file, display_popup, rename_htf_files
import sys
from tkinter import messagebox
# Constants
# DEFAULT_PATH_HTF1 = r'E:\B'
DEFAULT_PATH_HTF2 = r'D:\D'
BL2_SCHEDULE_PATH = r'C:\Users\tracab\Desktop\BL2_HTF_Schedule.xlsx'
ALLOWED_FILE_TYPES = ("MP4 files", "*.mp4")

# Add this at the beginning of your script
logging.basicConfig(level=logging.INFO)

# latest_htf1 = choose_file(DEFAULT_PATH_HTF1, title="HTF_1", allowed_types=("MP4 files", "*.mp4"), keyword='_1.mp4')
latest_htf2 = choose_file(DEFAULT_PATH_HTF2, title="HTF_2", allowed_types=("MP4 files", "*.mp4"), keyword='_2.mp4')

match = latest_htf2[-13:-6].replace('_', '-')

bl2_schedule = pd.read_excel(BL2_SCHEDULE_PATH, header=1)

# Right/Left is seen from the benches => Default: left == HTF2
new_htf2 = bl2_schedule.loc[bl2_schedule['3LC'] == match]['High Behind Left'].values[0]
# new_htf1 = bl2_schedule.loc[bl2_schedule['3LC'] == match]['High Behind Right'].values[0]

# Rename the available HTFs
try:
    new_htf2 = bl2_schedule.loc[bl2_schedule['3LC'] == match]['High Behind Left'].values[0]
except IndexError:
    messagebox.showwarning('Invalid 3LC in selected file/-s',
                           f'Please select the correct file/-s and check the 3LC!')
    sys.exit()

rename_htf_files(latest_htf2, DEFAULT_PATH_HTF2, new_htf2)

# Display popup window with information
display_popup("Renaming HTFs", "File has been successfully renamed!")
sys.exit()