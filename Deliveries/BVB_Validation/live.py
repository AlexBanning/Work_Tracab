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
v1.3: 2024/03/08 10:20
    - Adjusted script, so it can now be used in a live context for the usual workflow
    - Now works 100% identical to Falk's version and returns an identical named xlsx
    - Ideas for future: Implement a warning if the TDF did not contain any clicks
"""
import os
from TracabModules.Internal.data_output import get_player_stats, write_excel
from TracabModules.Internal.gamelog_functions import get_match_info

# Define main_folder in which the application is located
main_folder = os.getcwd()
# Define name of gamelog
gamelog = [x for x in os.listdir(main_folder + r'\Live_DFL') if 'Gamelog.xml' in x][0]
# Get necessary match_info out of gamelog
match_info = get_match_info(main_folder + r'\Live_DFL' + '\\' + gamelog)

# Get DFL-Files
dfl_folder = os.getcwd() + r'\Live_DFL\Webmonitor\Game_' + match_info['match_id'] + r'_3\Live\Team\Player'
files_dfl = [x for x in os.listdir(dfl_folder) if 'Resolution.xml' in x]

# Get EPL-Files
epl_folder = os.getcwd() + r'\Live_EPL\Webmonitor\Game_' + match_info['match_id'] + r'_2\Live\Team\Player'
files_epl = [x for x in os.listdir(epl_folder) if 'Resolution.xml' in x]

# Create DFs for all four Excel-sheets
bvb_dfl, oppo_dfl = get_player_stats(main_folder, files_dfl, gamelog, 'DFL', match_info)
bvb_epl, oppo_epl = get_player_stats(main_folder, files_epl, gamelog, 'EPL', match_info)

os.chdir(main_folder)
# Write Excel-file
write_excel([bvb_dfl, oppo_dfl], [bvb_epl, oppo_epl], match_info)
