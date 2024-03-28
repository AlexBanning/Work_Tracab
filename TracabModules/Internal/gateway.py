import os
from requests.structures import CaseInsensitiveDict
import requests
import logging
import json

# Create header
TOKEN = 'MGZhNjQ2ZTQ2NmQwOGFkNGE2NDYzMTlkNDFhN2FiNDUzZjgwZGIyYjhjNGNlNGMwODhmZDY1YjNmNjQ2YjdkZA=='
USER_ID = '360'
HEADERS = CaseInsensitiveDict()
HEADERS['accept'] = 'application/json'
HEADERS['Authorization'] = 'Bearer ' + TOKEN


def download_dat_file(game_id, vendor_id, data_quality, extr_version, headers=HEADERS, file_location=os.getcwd()):
    logging.basicConfig(level=logging.INFO)

    url = (f'https://api.tracab.com/api/V1/downloads/dat?GameID={game_id}&VendorID={vendor_id}&'
           f'ExtractionVersion={extr_version}&DataQuality={data_quality}&Phase=0')
    response = requests.get(url, headers=headers)
    dat_text = response.text

    with open(f'{file_location}\\{game_id}.dat', 'w') as f:
        f.write(dat_text)
        f.close()

    return logging.info(f'Dat-File for GameID {game_id} has been saved to {file_location}')


def download_metadata_file(game_id, vendor_id, data_quality, extr_version, headers=HEADERS, file_location=os.getcwd()):
    logging.basicConfig(level=logging.INFO)

    url = (f'https://api.tracab.com/api/V1/feeds/game_metadata?GameID={game_id}&VendorID={vendor_id}&'
           f'ExtractionVersion={extr_version}&DataQuality={data_quality}&Phase=0')
    response = requests.get(url, headers=headers).json()

    with open(f'{file_location}\\{game_id}.json', 'w') as f:
        json.dump(response, f)

    return logging.info(f'Metadata-File for GameID {game_id} has been saved to {file_location}')


def download_tf08_feed(game_id, vendor_id, data_quality, extr_version, headers=HEADERS):
    url = (f'https://api.tracab.com/api/V1/feeds/tf08?GameID={game_id}&VendorID={vendor_id}'
           f'&ExtractionVersion={extr_version}&DataQuality={data_quality}'
           )
    response = requests.get(url, headers=headers)
    data = json.loads(response.content.decode('utf8'))

    return data, logging.info(f'TF08 Feed for GameID {game_id} has been downloaded')


def download_tf09_feed(game_id, vendor_id, data_quality, extr_version, headers=HEADERS):
    url = (f'https://api.tracab.com/api/V1/feeds/tf09?GameID={game_id}&VendorID={vendor_id}'
           f'&ExtractionVersion={extr_version}&DataQuality={data_quality}'
           )
    response = requests.get(url, headers=headers)
    data = json.loads(response.content.decode('utf8'))

    return data, logging.info(f'TF08 Feed for GameID {game_id} has been downloaded')


def download_tf05_feed(game_id, vendor_id, data_quality, extr_version, headers=HEADERS):
    url = (f'https://api.tracab.com/api/V1/feeds/tf05?GameID={game_id}&VendorID={vendor_id}'
           f'&ExtractionVersion={extr_version}&DataQuality={data_quality}'
           )
    response = requests.get(url, headers=headers)
    data = json.loads(response.content.decode('utf8'))

    return data, logging.info(f'TF08 Feed for GameID {game_id} has been downloaded')
