"""
Generating a PDF out of Tracab's Gateway output.
1. Fetch all relevant KPIs 
2. Manipulate KPIs into the correct format for the PDF
3. Generate the PDF
"""
from TracabModules.Internal.gateway import download_tf08_feed, download_tf09_feed


game_id = '2374222'
vendor_id = '5'
extr_vers = '4'
data_quality = '1'

tf09_data = download_tf09_feed(game_id, vendor_id, data_quality, extr_vers)
tf08_data = download_tf08_feed(game_id, vendor_id, data_quality, extr_vers)




