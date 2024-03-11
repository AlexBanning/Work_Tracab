"""
Purpose of this code will be to extract all necessary KPIs needed for the BVB_excel sheet out of the output files
and create the xlsx-file.

v1.0: 2024/03/11 10:00
    - Copied version of live.py that has been adjusted where necessary to create the observed-xlsx file
"""
import os
from TracabModules.Internal.data_output import get_player_stats, write_excel
from TracabModules.Internal.gamelog_functions import get_match_info

# Define main_folder in which the application is located
main_folder = os.getcwd()
# Define name of gamelog
gamelog = [x for x in os.listdir(main_folder + r'\Observed_DFL') if 'Gamelog.xml' in x][0]
# Get necessary match_info out of gamelog
match_info = get_match_info(main_folder + r'\Observed_DFL' + '\\' + gamelog)

# Get DFL-Files
dfl_folder = os.getcwd() + r'\Observed_DFL\Webmonitor\Game_' + match_info['match_id'] + r'_3\Observed\Team\Player'
files_dfl = [x for x in os.listdir(dfl_folder) if 'Resolution.xml' in x]

# Get EPL-Files
epl_folder = os.getcwd() + r'\Observed_EPL\Webmonitor\Game_' + match_info['match_id'] + r'_2\Observed\Team\Player'
files_epl = [x for x in os.listdir(epl_folder) if 'Resolution.xml' in x]

# Create DFs for all four Excel-sheets
bvb_dfl, oppo_dfl = get_player_stats(main_folder, files_dfl, gamelog, 'DFL', obs=True, match_info=match_info)
bvb_epl, oppo_epl = get_player_stats(main_folder, files_epl, gamelog, 'EPL', obs=True, match_info=match_info)

os.chdir(main_folder)
# Write Excel-file
write_excel([bvb_dfl, oppo_dfl], [bvb_epl, oppo_epl], match_info, obs=True)
