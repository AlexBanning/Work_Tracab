"""
Renaming the HTFs in the BL1 and BL2 requires:
    - Knowing which game has been played
    - The name/location of both HTFs that were generated
        ~ HTF_1 always on D: and HTF_2 always on E: (EXCEPT AUGSBURG; CURRENTLY ONLY E AVAILABLE)
    - STS-ID of the match
        ~ Load in the sts file and fetch necessary information
"""

import pandas as pd
import os
import glob
from TracabModules.Internal.server_manipulations import newest
# bl1_schedule = pd.read_excel(r'C:\Users\a.banning\Desktop\BL1_HTF_Schedule.xlsx')

list_of_files = glob.glob(r'C:/Users/a.banning/Desktop/*')
latest_file = max(list_of_files, key=os.path.getctime)
