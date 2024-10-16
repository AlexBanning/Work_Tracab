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
v1.0: 2024/04/16 17:00
    - First version that could be used by the end user.
    - Design and amount of KPIs not final yet.
"""

from TracabModules.Internal.gateway import FeedStatusGUI, FootballDataProcessor
import threading

"""
Definition of game parameters
"""
EXTR_VERS = '4'
DATA_QUALITY = '0'

"""
Feed-status overview 
"""
app = FeedStatusGUI(DATA_QUALITY, EXTR_VERS)


"""
Live Stream Data
"""
if __name__ == "__main__":
    processor = FootballDataProcessor(game_id=185101, vendor_id=4, protocol='JSON')

    # Start fetching data in a separate thread
    fetch_thread = threading.Thread(target=processor.fetch_data)
    fetch_thread.start()

    # Start processing data in another thread
    process_thread = threading.Thread(target=processor.process_data)
    process_thread.start()

