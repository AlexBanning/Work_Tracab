"""
Purpose of this code will be to extract all necessary KPIs needed for the BVB_excel sheet out of the output files
and create the xlsx-file.

v1.0: 2024/03/06:
    - Creation of the xlsx-file already possible
    - Formatting is not identical to Falk's application
"""
import os
import pandas as pd
from TracabModules.Internal.data_output import get_player_stats

# os.getcwd()
os.chdir(r'C:\Users\a.banning\Desktop\BVB_Test')
files_dfl = os.listdir(os.getcwd() + r'\Players_DFL')
files_epl = os.listdir(os.getcwd() + r'\Players_EPL')
gamelog = [x for x in os.listdir(os.getcwd()) if 'Gamelog.xml' in x][0]

bvb_dfl, oppo_dfl = get_player_stats(files_dfl, gamelog, 'DFL')
bvb_epl, oppo_epl = get_player_stats(files_epl, gamelog, 'EPL')


# Write Excel-File. Would need some formatting and additional information to match Falk's application 100%
writer = pd.ExcelWriter("Test.xlsx", engine="xlsxwriter")

# Write each dataframe to a different worksheet.
bvb_epl.to_excel(writer, sheet_name="BVB_Live_EPL")
oppo_epl.to_excel(writer, sheet_name="Opp_Live_EPL")
bvb_dfl.to_excel(writer, sheet_name="BVB_Live_DFL")
oppo_dfl.to_excel(writer, sheet_name="Opp_Live_DFL")


# Close the Pandas Excel writer and output the Excel file.
writer.close()
