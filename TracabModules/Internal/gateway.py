
from requests.structures import CaseInsensitiveDict
import requests
import logging
import json
import tkinter as tk
import threading

# Create header
TOKEN = 'MGZhNjQ2ZTQ2NmQwOGFkNGE2NDYzMTlkNDFhN2FiNDUzZjgwZGIyYjhjNGNlNGMwODhmZDY1YjNmNjQ2YjdkZA=='
USER_ID = '360'
HEADERS = CaseInsensitiveDict()
HEADERS['accept'] = 'application/json'
HEADERS['Authorization'] = 'Bearer ' + TOKEN


class GatewayDownloader:
    def __init__(self, game_id, vendor_id, data_quality, extr_vers):
        self.game_id = game_id
        self.vendor_id = vendor_id
        self.data_quality = data_quality
        self.extr_version = extr_vers
        self.headers = HEADERS

    def _make_request(self, url):
        response = requests.get(url, headers=self.headers)
        success = response.status_code == 200
        return response, success

    def download_ascii_feed(self):
        logging.basicConfig(level=logging.INFO)
        url = (f'https://api.tracab.com/api/V1/downloads/dat?GameID={self.game_id}&VendorID={self.vendor_id}&'
               f'ExtractionVersion={self.extr_version}&DataQuality={self.data_quality}&Phase=0')
        response, success = self._make_request(url)
        if success:
            logging.info(f'The ASCII-feed for GameID {self.game_id} has been downloaded')
            return response, success
        else:
            return logging.info(f'Error: {response.status_code}')

    def download_json_feed(self, max_bytes=1024):
        logging.basicConfig(level=logging.INFO)
        url = (f'https://api.tracab.com/api/V1/downloads/tf10?GameID={self.game_id}&VendorID={self.vendor_id}&'
               f'ExtractionVersion={self.extr_version}&DataQuality={self.data_quality}&Phase=0')

        try:
            with requests.get(url, stream=True) as response:
                response.raise_for_status()  # Raise an exception for HTTP errors

                # Read data in chunks
                downloaded_data = b""
                for chunk in response.iter_content(chunk_size=max_bytes):
                    downloaded_data += chunk
                    if len(downloaded_data) >= max_bytes:
                        break  # Limiting the active download time by exiting the loop when max_bytes is reached

                logging.info(f'The json-feed for GameID {self.game_id} has been downloaded')
                return downloaded_data, True
        except requests.exceptions.RequestException as e:
            logging.error(f'Error: {e}')
            return None, False

    def download_binary_feed(self):
        logging.basicConfig(level=logging.INFO)

        url = (f'https://api.tracab.com/api/V1/downloads/tbf?GameID={self.game_id}&VendorID={self.vendor_id}&'
               f'ExtractionVersion={self.extr_version}&DataQuality={self.data_quality}&Phase=0')
        response, success = self._make_request(url)

        if success:
            logging.info(f'The binary-feed for GameID {self.game_id} has been downloaded')
            return response, success
        #else:
        #    return logging.info(f'Error: {response.status_code}')

    def download_metadata_file(self):

        url = (f'https://api.tracab.com/api/V1/feeds/game_metadata?GameID={self.game_id}&VendorID={self.vendor_id}&'
               f'ExtractionVersion={self.extr_version}&DataQuality={self.data_quality}&Phase=0')
        response, success = self._make_request(url)
        if success:
            logging.info(f'The metadata for GameID {self.game_id} has been downloaded')
            return response, success
        else:
            return logging.info(f'Error: {response.status_code}')

    def download_tf08_feed(self):
        logging.basicConfig(level=logging.INFO)

        url = (f'https://api.tracab.com/api/V1/feeds/tf08?GameID={self.game_id}&VendorID={self.vendor_id}'
               f'&ExtractionVersion={self.extr_version}&DataQuality={self.data_quality}'
               )
        response, success = self._make_request(url)
        data = json.loads(response.content.decode('utf8'))

        if success:
            logging.info(f'TF08 Feed for GameID {self.game_id} has been downloaded')
            return data, success
        else:
            return (logging.info(f'TF08 Feed for GameID {self.game_id} is not available'),
                    logging.info(f'Error: {data['status']}, Message: {data['message']}'))

    def download_tf09_feed(self):
        logging.basicConfig(level=logging.INFO)

        url = (f'https://api.tracab.com/api/V1/feeds/tf09?GameID={self.game_id}&VendorID={self.vendor_id}'
               f'&ExtractionVersion={self.extr_version}&DataQuality={self.data_quality}'
               )
        response, success = self._make_request(url)
        data = json.loads(response.content.decode('utf8'))

        if success:
            logging.info(f'TF09 Feed for GameID {self.game_id} has been downloaded')
            return data, success
        else:
            return (logging.info(f'TF09 Feed for GameID {self.game_id} is not available'),
                    logging.info(f'Error: {data['status']}, Message: {data['message']}'))

    def download_tf05_feed(self):
        logging.basicConfig(level=logging.INFO)

        url = (f'https://api.tracab.com/api/V1/feeds/tf05?GameID={self.game_id}&VendorID={self.vendor_id}'
               f'&ExtractionVersion={self.extr_version}&DataQuality={self.data_quality}'
               )
        response, success = self._make_request(url)
        data = json.loads(response.content.decode('utf8'))

        if success:
            logging.info(f'TF05 Feed for GameID {self.game_id} has been downloaded')
            return data, success
        else:
            return (logging.info(f'TF05 Feed for GameID {self.game_id} is not available'),
                    logging.info(f'Error: {data['status']}, Message: {data['message']}'))


class FeedStatusGUI:
    def __init__(self, game_id, vendor_id, data_quality, extr_vers):
        self.downloader = GatewayDownloader(game_id, vendor_id, data_quality, extr_vers)
        self.feed_status = {
            'Metadata': False,
            'ASCII': False,
            'JSON': False,
            'TF05': False,
            'TF09': False,
            'TF08': False
        }

        self.root = tk.Tk()
        self.root.title("Feed Status")

        self.status_labels = {}
        self.progress_bars = {}

        self.create_widgets()

        # Create button to enable upcoming functions
        self.enable_button = tk.Button(self.root, text="Check Feeds", command=self.check_feeds)
        self.enable_button.grid(row=len(self.feed_status), column=0, columnspan=2, pady=10)

        self.root.mainloop()

    def create_widgets(self):
        for i, (feed, status) in enumerate(self.feed_status.items()):
            label_text = f"{feed}: {'Available' if status else 'Not available'}"
            self.status_labels[feed] = tk.Label(self.root, text=label_text)
            self.status_labels[feed].grid(row=i, column=0, padx=10, pady=5)

            color = "green" if status else "red"
            self.status_labels[feed].configure(bg=color, fg="white")

    def check_feeds(self):

        thread = threading.Thread(target=self.execute_download_functions)
        thread.start()

    def execute_download_functions(self):
        metadata_response, metadata_success = self.downloader.download_metadata_file()
        self.update_feed_status('Metadata', metadata_success)

        ascii_response, ascii_success = self.downloader.download_ascii_feed()
        self.update_feed_status('ASCII', ascii_success)

        json_response, json_success = self.downloader.download_json_feed()
        self.update_feed_status('JSON', json_success)

        tf05_data, tf05_success = self.downloader.download_tf05_feed()
        self.update_feed_status('TF05', tf05_success)

        tf09_data, tf09_success = self.downloader.download_tf09_feed()
        self.update_feed_status('TF09', tf09_success)

        tf08_data, tf08_success = self.downloader.download_tf08_feed()
        self.update_feed_status('TF08', tf08_success)

        if all((metadata_success, ascii_success, json_success, tf05_success, tf09_success, tf08_success)):
            self.enable_upcoming_functions()

    def update_feed_status(self, feed, success):
        if success:
            self.status_labels[feed].configure(text=f"{feed}: Available", bg="green", fg="white")
            self.feed_status[feed] = True
        else:
            self.status_labels[feed].configure(text=f"{feed}: Not available", bg="red", fg="white")
            self.feed_status[feed] = False

    def enable_upcoming_functions(self):
        print("Functions enabled. You can now perform data manipulation and calculations.")


