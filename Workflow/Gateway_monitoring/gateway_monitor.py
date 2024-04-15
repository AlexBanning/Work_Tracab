"""
The purpose of this code will be to enable the monitoring of basic KPIs out of the GW output to ensure that the GW
delivery is working successfully.

Goal: Show the most basic KPIS (Team total distance, possession %, team's topspeed), but also provide information if all
      feeds are available and possible to be fetched

v0.1: 2024/04/8 22:30
    - Very rough version of a GUI that indicates if a feed is available of not.
    - FeedStatusGUI needs to be adjusted so that the necessary data gets returned after a successful download
    - Try to limit the download size of json files, maybe stream of 'stream-api.tracab.com' might work for this one,
      including start and end subscription.
v0.2: 2024/04/09 21:00
    - First version of GUI that returns the availability of all used feeds and first team information in terms of home
      and away names
    - Cannot work with the 202 response for ASCII feeds, need to implement some loop that it retries until feed has been
      processed.
v0.3: 2024/04/10 16:00
    - Further developed version that not only shows distance and possession, but also already in some kind of readable
      form.
v0.5: 2024/04/15 14:30
    - User is now able to manually define the VendorID and GameID.
    - Update button for KPIs has been introduced. Needs to be tested during a live game.
"""

from TracabModules.Internal.gateway import FeedStatusGUI

"""
Definition of game parameters
"""
EXTR_VERS = '4'
DATA_QUALITY = '0'

"""
Feed-status overview 
"""
app = FeedStatusGUI(DATA_QUALITY, EXTR_VERS)
