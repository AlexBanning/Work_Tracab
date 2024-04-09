"""
The purpose of this code will be to enable the monitoring of basic KPIs out of the GW output to ensure that the GW
delivery is working successfully.

Goal: Show the most basic KPIS (Team total distance, possession %, team's topspeed), but also provide information if all
      feeds are available and possible to be fetched

v0.1: Very rough version of a GUI that indicates if a feed is available of not.
    - FeedStatusGUI needs to be adjusted so that the necessary data gets returned after a successful download
    - Try to limit the download size of json files, maybe stream of 'stream-api.tracab.com' might work for this one,
      including start and end subscription.
v0.2: First version of GUI that returns the availability of all used feeds and first team information in terms of home
      and away names
"""

from TracabModules.Internal.gateway import GatewayDownloader, FeedStatusGUI

"""
Definition of game parameters
"""
EXTR_VERS = '4'
DATA_QUALITY = '0'

# GameID and VendorID should be user-defined in the final version
game_id = '186491'
vendor_id = '4'


"""
Connect to GW to check if all feeds are available
"""
downloader = GatewayDownloader(game_id, vendor_id, DATA_QUALITY, EXTR_VERS)
metadata_response, metadata_success,  = downloader.download_metadata_file()
ascii_response, ascii_success,  = downloader.download_ascii_feed()
json_response, json_success,  = downloader.download_json_feed()

tf05_data, tf05_success = downloader.download_tf05_feed()
tf09_data, tf09_success = downloader.download_tf09_feed()
tf08_data, tf08_success = downloader.download_tf08_feed()

"""
Feed-status overview 
"""
app = FeedStatusGUI(game_id, vendor_id, DATA_QUALITY, EXTR_VERS)
