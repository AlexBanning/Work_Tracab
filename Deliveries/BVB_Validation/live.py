"""
Purpose of this code will be to extract all necessary KPIs needed for the BVB_excel sheet out of the output files
and create the xlsx-file.

v1.0: 2024/03/06 16:00:00
    - Creation of the xlsx-file already possible
    - Formatting is not identical to Falk's application
v1.1: 2024/03/06 17:30:00
    - Implemented format settings
    - Currently only for one sheet, needs to be applied in an efficient manner to the others, too.
v1.2: 2024/03/07 09:45
    - Implemented format settings for all sheets
    - Adjusted TopSpeed-KPI to show actual top speed of the match
    - Added additional functions to be able to write the Excel completely automatically from gamelog and
      PlayerID_Resolution files
"""
import os
import pandas as pd
from TracabModules.Internal.data_output import get_player_stats, write_excel

# os.getcwd()
os.chdir(r'C:\Users\a.banning\Desktop\BVB_Test')
files_dfl = os.listdir(os.getcwd() + r'\Players_DFL')
files_epl = os.listdir(os.getcwd() + r'\Players_EPL')
gamelog = [x for x in os.listdir(os.getcwd()) if 'Gamelog.xml' in x][0]

bvb_dfl, oppo_dfl = get_player_stats(files_dfl, gamelog, 'DFL')
bvb_epl, oppo_epl = get_player_stats(files_epl, gamelog, 'EPL')

# Write Excel-File
write_excel([bvb_dfl, oppo_dfl], [bvb_epl, oppo_epl], gamelog)



