from requests.structures import CaseInsensitiveDict
from TracabModules.DataManipulation.data_manipulation import GatewayKPIs
import requests
import logging
import json
import tkinter as tk
from tkinter import ttk
import threading
import time

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

        while response.status_code == 202:
            logging.info(f"Received status code 202. Retrying in 10 seconds...")
            time.sleep(10)  # Wait for 10 seconds before retrying
            response, success = self._make_request(url)

        if success:
            logging.info(f'The ASCII-feed for GameID {self.game_id} has been downloaded')
            return response, success
        else:
            return logging.info(f'Error: {response.status_code}')

    def download_json_feed(self):
        logging.basicConfig(level=logging.INFO)
        url = (f'https://api.tracab.com/api/V1/downloads/tf10?GameID={self.game_id}&VendorID={self.vendor_id}&'
               f'ExtractionVersion={self.extr_version}&DataQuality={self.data_quality}&Phase=0')
        response, success = self._make_request(url)
        if success:
            logging.info(f'The JSON-feed for GameID {self.game_id} has been downloaded')
            return response, success
        else:
            return logging.info(f'Error: {response.status_code}')

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
        while response.status_code == 202:
            logging.info(f"Received status code 202. Retrying in 5 seconds...")
            time.sleep(5)  # Wait for 10 seconds before retrying
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
    def __init__(self, data_quality, extr_vers):
        self.check_feeds_button = None
        self.data_quality = data_quality
        self.extr_version = extr_vers
        self.downloader = None
        self.calculator = None
        self.feed_status = {
            'Metadata': False,
            'ASCII': False,
            'JSON': False,
            'TF05': False,
            'TF09': False,
            'TF08': False,
        }

        self.teams = {
            'Home': None,
            ' vs.': None,
            'Away': None
        }

        self.distances = {
            'Home Distance': None,
            'Distance': 'Distance',
            'Away Distance': None
        }

        self.possession = {
            'Home Possession': None,
            'Possession': 'Possession',
            'Away Possession': None
        }

        self.root = tk.Tk()
        self.root.title("Feed Status")
        self.root.configure(bg='#2F4F4F')

        # Adjust the size of the GUI window
        self.root.geometry("560x350")

        # Create a frame to contain the labels and buttons
        self.center_frame = tk.Frame(self.root)
        self.center_frame.grid(row=0, column=0, padx=10, pady=10)
        self.center_frame.configure(bg='#2F4F4F')

        self.status_labels = {}
        self.team_labels = {}
        self.distance_labels = {}
        self.possession_labels = {}
        self.progress_bars = {}

        self.create_widgets()

        self.root.mainloop()

    def create_widgets(self):
        # Progress bar
        self.progress = ttk.Progressbar(self.center_frame, orient="horizontal", mode="determinate")
        self.progress.grid(row=len(self.feed_status) + 4, column=0, pady=5, sticky="ew")

        # Entry widgets for GameID and VendorID
        tk.Label(self.center_frame, text="GameID:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.game_id_entry = tk.Entry(self.center_frame)
        self.game_id_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(self.center_frame, text="VendorID:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.vendor_id_entry = tk.Entry(self.center_frame)
        self.vendor_id_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Button to set GameID and VendorID
        self.set_ids_button = tk.Button(self.center_frame, text="Get Feeds", command=self.set_ids)
        self.set_ids_button.grid(row=2, column=0, columnspan=1, pady=5, sticky="ew")

        for i, (feed, status) in enumerate(self.feed_status.items()):
            feed_label_text = f"{feed} {'Available' if status else ''}"
            self.status_labels[feed] = tk.Label(self.center_frame, text=feed_label_text)
            self.status_labels[feed].grid(row=i+4, column=0, padx=10, pady=5, sticky="nsew")

            color = "green" if status else "red"
            self.status_labels[feed].configure(bg=color, fg="white")

        # # Create button to check all feeds
        # self.check_feeds_button = tk.Button(self.center_frame, text="Check All Feeds", command=self.check_feeds)
        # self.check_feeds_button.grid(row=len(self.feed_status) + 1, column=0, pady=10, sticky="nsew")

        # Add Text widget to display Team Names
        for i, (team, name) in enumerate(self.teams.items()):
            team_label_text = f"{team}"
            self.team_labels[team] = tk.Label(self.center_frame, text=team_label_text)
            self.team_labels[team].grid(row=0, column=i + 3, padx=10, pady=5, sticky="nsew")
            self.team_labels[team].configure(bg="#2F4F4F", fg="#98FB98")

        for i, (team, dist) in enumerate(self.distances.items()):
            distance_label_text = f"{team}"
            self.distance_labels[team] = tk.Label(self.center_frame, text=distance_label_text)
            self.distance_labels[team].grid(row=1, column=i+3, padx=10, pady=5, sticky="nsew")
            self.distance_labels[team].configure(bg="#2F4F4F", fg="#98FB98")

        for i, (team, possession) in enumerate(self.possession.items()):
            possession_label_text = f"{team}"
            self.possession_labels[team] = tk.Label(self.center_frame, text=possession_label_text)
            self.possession_labels[team].grid(row=2, column=i+3, padx=10, pady=5, sticky="nsew")
            self.possession_labels[team].configure(bg="#2F4F4F", fg="#98FB98")

        #Add update KPIs button
        self.update_button = tk.Button(self.center_frame, text='Update', command=self.update_kpi_function)
        self.update_button.grid(row=3, column=3, padx=10, pady=5, sticky="nsew")

    def check_json_feed(self):
        # Execute function to check JSON feed availability
        json_response, json_success = self.downloader.download_json_feed()
        if json_success:
            self.status_labels['JSON'].config(text="JSON: Available", bg="green", fg="white")
            self.feed_status['JSON'] = True
        else:
            self.status_labels['JSON'].config(text="JSON", bg="red", fg="white")
            logging.error("JSON feed is not available")

    def set_ids(self):
        self.game_id = self.game_id_entry.get()
        self.vendor_id = self.vendor_id_entry.get()

        self.downloader = GatewayDownloader(self.game_id, self.vendor_id, self.data_quality, self.extr_version)

        logging.info(f"GameID set to {self.game_id} and VendorID set to {self.vendor_id}")

        # Start checking feeds after setting IDs
        self.check_feeds()

    def check_feeds(self):
        thread = threading.Thread(target=self.execute_download_functions)
        thread.start()

    def execute_download_functions(self):
        self.progress['value'] = 0  # Reset progress bar
        self.progress['maximum'] = 100  # Set maximum value

        metadata_response, metadata_success = self.downloader.download_metadata_file()
        self.update_feed_status('Metadata', metadata_success)
        self.progress.step(16.7)  # Simulate progress

        ascii_response, ascii_success = self.downloader.download_ascii_feed()
        self.update_feed_status('ASCII', ascii_success)
        self.progress.step(16.7)  # Simulate progress

        # json_response, json_success = self.downloader.download_json_feed()
        # self.update_feed_status('JSON', json_success)
        # self.progress.step(16.7)  # Simulate progress

        tf05_data, tf05_success = self.downloader.download_tf05_feed()
        self.update_feed_status('TF05', tf05_success)
        self.progress.step(16.7)  # Simulate progress

        tf09_data, tf09_success = self.downloader.download_tf09_feed()
        self.update_feed_status('TF09', tf09_success)
        self.progress.step(16.7)  # Simulate progress

        tf08_data, tf08_success = self.downloader.download_tf08_feed()
        self.update_feed_status('TF08', tf08_success)
        self.progress.step(16.7)  # Simulate progress

        if all((metadata_success, ascii_success, tf05_success, tf09_success, tf08_success)):
            self.progress['value'] = self.progress['maximum']
            self.get_kpi_function(tf08_data)

    def update_feed_status(self, feed, success):
        if success:
            self.status_labels[feed].configure(text=f"{feed}: Available", bg="green", fg="white")
            self.feed_status[feed] = True
        else:
            self.status_labels[feed].configure(text=f"{feed}: Not available", bg="red", fg="white")
            self.feed_status[feed] = False

    def update_team_name(self, team, name):
        self.team_labels[team].configure(text=f"{name}", bg="#2F4F4F", fg="#98FB98")

    def update_team_distance(self, team, distance):
        self.distance_labels[team].configure(text=f"{distance} km", bg="#2F4F4F", fg="#98FB98")

    def update_team_possession(self, team, possession):
        self.possession_labels[team].configure(text=f"{possession} %", bg="#2F4F4F", fg="#98FB98")

    def get_kpi_function(self, tf08_data):
        self.calculator = GatewayKPIs(tf08_data, kpi_list_tf08=['Possession', 'Distance'])
        kpis = self.calculator.get_tf08_kpis()
        self.update_team_name('Home', list(kpis.keys())[0])
        self.update_team_name('Away', list(kpis.keys())[1])
        self.update_team_distance('Home Distance', list(kpis.values())[0]['Distance'])
        self.update_team_distance('Away Distance', list(kpis.values())[1]['Distance'])
        self.update_team_possession('Home Possession', list(kpis.values())[0]['Possession'])
        self.update_team_possession('Away Possession', list(kpis.values())[1]['Possession'])

    def update_kpi_function(self):
        logging.basicConfig(level=logging.INFO)
        tf08_data, tf08_success = self.downloader.download_tf08_feed()
        self.update_feed_status('TF08', tf08_success)
        self.get_kpi_function(tf08_data)
        logging.info(f'The values for {self.game_id} have been updated')


