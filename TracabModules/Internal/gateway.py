from requests.structures import CaseInsensitiveDict
from TracabModules.DataManipulation.data_manipulation import GatewayKPIs
import numpy as np
import pandas as pd
import requests
import logging
import json
import socket
import struct
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from PIL import ImageTk, Image
from tkinter import font as tkfont
import threading
import time
import queue

# Create header
TOKEN = 'MGZhNjQ2ZTQ2NmQwOGFkNGE2NDYzMTlkNDFhN2FiNDUzZjgwZGIyYjhjNGNlNGMwODhmZDY1YjNmNjQ2YjdkZA=='
USER_ID = '360'
HEADERS = CaseInsensitiveDict()
HEADERS['accept'] = 'application/json'
HEADERS['Authorization'] = 'Bearer ' + TOKEN


class GatewayDownloader:
    def __init__(self, game_id, vendor_id, data_quality, extr_vers, protocol=None):
        # All Feeds
        self.game_id = game_id
        self.vendor_id = vendor_id
        self.data_quality = data_quality
        self.extr_version = extr_vers
        self.headers = HEADERS

        # Live Data
        self.protocol = protocol
        self.data_queue = queue.Queue()

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

        while response.status_code == 202:
            logging.info(f"Received status code 202. Retrying in 10 seconds...")
            time.sleep(10)  # Wait for 10 seconds before retrying
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

        while response.status_code == 202:
            logging.info(f"Received status code 202. Retrying in 10 seconds...")
            time.sleep(10)  # Wait for 10 seconds before retrying
            response, success = self._make_request(url)

        if success:
            logging.info(f'The binary-feed for GameID {self.game_id} has been downloaded')
            return response, success
        # else:
        #    return logging.info(f'Error: {response.status_code}')

    def download_metadata_file(self):

        url = (f'https://api.tracab.com/api/V1/feeds/game_metadata?GameID={self.game_id}&VendorID={self.vendor_id}&'
               f'ExtractionVersion={self.extr_version}&DataQuality={self.data_quality}&Phase=0')
        response, success = self._make_request(url)

        while response.status_code == 202:
            logging.info(f"Received status code 202. Retrying in 10 seconds...")
            time.sleep(10)  # Wait for 10 seconds before retrying
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

        while response.status_code == 202:
            logging.info(f"Received status code 202. Retrying in 5 seconds...")
            time.sleep(5)  # Wait for 10 seconds before retrying
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

        while response.status_code == 202:
            logging.info(f"Received status code 202. Retrying in 5 seconds...")
            time.sleep(5)  # Wait for 10 seconds before retrying
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
            '': None,
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

        self.speed = {
            'Home Speed': None,
            'Top Speed': 'Top Speed',
            'Away Speed': None
        }

        self.root = tk.Tk()
        self.root.title("Feed Status")
        self.root.iconbitmap("Tracab.ico")
        self.root.configure(bg='#2F4F4F')

        # Adjust the size of the GUI window
        self.root.geometry("560x350")

        # Create a frame to contain the labels and buttons
        self.center_frame = tk.Frame(self.root)
        self.center_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.center_frame.configure(bg='#2F4F4F')

        # Configure row and column weights for center_frame
        for i in range(len(self.feed_status) + 5):  # +5 for labels, entries, and progress bar
            self.center_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):  # Assuming 4 columns for labels and entries
            self.center_frame.grid_columnconfigure(i, weight=1)

        self.status_labels = {}
        self.team_labels = {}
        self.distance_labels = {}
        self.possession_labels = {}
        self.speed_labels = {}
        self.progress_bars = {}

        self.create_widgets()

        # Adjust the window geometry
        self.adjust_window_size()

        # Create a new window for logging
        self.create_logging_window()

        # Set up logging
        self.setup_logging()

        self.root.mainloop()

    def create_logging_window(self):
        # Create a new window for logging
        self.logging_window = tk.Toplevel(self.root)
        self.logging_window.title("Logging")
        self.logging_window.geometry("500x200")

        # Initially withdraw the window
        self.logging_window.withdraw()

        # Create Text widget for logging
        self.log_text = tk.Text(self.logging_window, wrap=tk.WORD, height=20, width=100)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def setup_logging(self):
        # Create handler and add to root logger
        self.logging_handler = TextHandler(self.log_text)
        logging.getLogger().addHandler(self.logging_handler)
        logging.getLogger().setLevel(logging.INFO)

    def toggle_logging_window(self):
        if self.logging_window.state() == "withdrawn":
            self.logging_window.deiconify()  # Show the window
        else:
            self.logging_window.withdraw()  # Hide the window

    def adjust_window_size(self):
        self.root.update_idletasks()  # Update the GUI to finish arranging widgets
        width = self.root.winfo_reqwidth()  # Get the required width of the GUI
        height = self.root.winfo_reqheight()  # Get the required height of the GUI
        self.root.geometry(f"{width}x{height}")  # Set the GUI window size

    def create_widgets(self):
        # Progress bar
        self.progress = ttk.Progressbar(self.center_frame, orient="horizontal", mode="determinate", length=150)
        self.progress.grid_remove()

        # Entry widgets for GameID and VendorID
        tk.Label(self.center_frame, text="GameID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.game_id_entry = tk.Entry(self.center_frame)
        self.game_id_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        tk.Label(self.center_frame, text="VendorID:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.vendor_id_entry = tk.Entry(self.center_frame)
        self.vendor_id_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Button to set GameID and VendorID
        self.set_ids_button = tk.Button(self.center_frame, text="Get Feeds", command=self.set_ids)
        self.set_ids_button.grid(row=2, column=0, pady=5, sticky="ew")

        self.toggle_button = tk.Button(self.center_frame, text="Toggle Log-Info", command=self.toggle_logging_window)
        self.toggle_button.grid(row=len(self.feed_status) + 5, column=5, columnspan=1, pady=10, sticky="ew")

        for i, (feed, status) in enumerate(self.feed_status.items()):
            feed_label_text = f"{feed} {'Available' if status else ''}"
            self.status_labels[feed] = tk.Label(self.center_frame, text=feed_label_text)
            self.status_labels[feed].grid(row=i + 4, column=0, padx=10, pady=5, sticky="nsew")

            color = "green" if status else "red"
            self.status_labels[feed].configure(bg=color, fg="white")

        # Add Text widget to display Team Names
        for i, (team, name) in enumerate(self.teams.items()):
            team_label_text = f"{team}"
            self.team_labels[team] = tk.Label(self.center_frame, text=team_label_text, font=tkfont.Font(weight='bold'))
            self.team_labels[team].grid(row=0, column=i + 3, padx=10, pady=5, sticky="nsew")
            self.team_labels[team].configure(bg="#2F4F4F", fg="#98FB98")
        # Add Text widget to display Team Distances
        for i, (team, dist) in enumerate(self.distances.items()):
            distance_label_text = f"{team}"
            self.distance_labels[team] = tk.Label(self.center_frame, text=distance_label_text)
            self.distance_labels[team].grid(row=1, column=i + 3, padx=10, pady=5, sticky="nsew")
            self.distance_labels[team].configure(bg="#2F4F4F", fg="#98FB98")
        # Add Text widget to display Team Possession
        for i, (team, possession) in enumerate(self.possession.items()):
            possession_label_text = f"{team}"
            self.possession_labels[team] = tk.Label(self.center_frame, text=possession_label_text)
            self.possession_labels[team].grid(row=2, column=i + 3, padx=10, pady=5, sticky="nsew")
            self.possession_labels[team].configure(bg="#2F4F4F", fg="#98FB98")
        # Add Text widget to display Team Top Speeds
        for i, (team, speed) in enumerate(self.speed.items()):
            speed_label_text = f"{team}"
            self.speed_labels[team] = tk.Label(self.center_frame, text=speed_label_text)
            self.speed_labels[team].grid(row=3, column=i + 3, padx=10, pady=5, sticky="nsew")
            self.speed_labels[team].configure(bg="#2F4F4F", fg="#98FB98")

        # Add update KPIs button
        self.update_button = tk.Button(self.center_frame, text='Update', command=self.update_kpi_function)
        self.update_button.grid(row=4, column=3, padx=10, pady=5, sticky="nsew")

        # Add button to toggle speed window
        self.toggle_speed_button = tk.Button(self.center_frame, text="Toggle Speeds", command=self.toggle_speed_window)
        self.toggle_speed_button.grid(row=5, column=3, padx=10, pady=5, sticky="nsew")

        # Adjust the window geometry
        self.root.update_idletasks()  # Update the window to get correct sizes
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        self.root.geometry(f"{width}x{height}")

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
        self.progress.grid(row=len(self.feed_status) + 4, column=0, pady=5, sticky="ew")
        self.progress['value'] = 0  # Reset progress bar
        self.progress['maximum'] = 100  # Set maximum value

        self.adjust_window_size()

        metadata_response, metadata_success = self.downloader.download_metadata_file()
        self.update_feed_status('Metadata', metadata_success)
        self.progress.step(16.7)  # Simulate progress

        self.adjust_window_size()

        ascii_response, ascii_success = self.downloader.download_ascii_feed()
        self.update_feed_status('ASCII', ascii_success)
        self.progress.step(16.7)  # Simulate progress

        json_response, json_success = self.downloader.download_json_feed()
        self.update_feed_status('JSON', json_success)
        self.progress.step(16.7)  # Simulate progress

        tf05_data, tf05_success = self.downloader.download_tf05_feed()
        self.update_feed_status('TF05', tf05_success)
        self.progress.step(16.7)  # Simulate progress

        tf09_data, tf09_success = self.downloader.download_tf09_feed()
        self.update_feed_status('TF09', tf09_success)
        self.progress.step(16.7)  # Simulate progress

        tf08_data, tf08_success = self.downloader.download_tf08_feed()
        self.update_feed_status('TF08', tf08_success)
        self.progress.step(16.7)  # Simulate progress

        self.progress.grid_remove()

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
        self.possession_labels[team].configure(text=f"{possession}%", bg="#2F4F4F", fg="#98FB98")

    def update_team_speed(self, team, speed):
        self.speed_labels[team].configure(text=f"{speed} km/h", bg="#2F4F4F", fg="#98FB98")

    def get_kpi_function(self, tf08_data):
        self.calculator = GatewayKPIs(tf08_data, kpi_list_tf08=['Possession', 'TopSpeedPlayer', 'Distance'])
        kpis = self.calculator.get_tf08_kpis()

        # Team Names
        self.update_team_name('Home', list(kpis.keys())[0])
        self.update_team_name('Away', list(kpis.keys())[1])
        # Team Distances
        self.update_team_distance('Home Distance', list(kpis.values())[0]['Distance'])
        self.update_team_distance('Away Distance', list(kpis.values())[1]['Distance'])
        # Team Possessions
        self.update_team_possession('Home Possession', list(kpis.values())[0]['Possession'])
        self.update_team_possession('Away Possession', list(kpis.values())[1]['Possession'])
        # TopSpeed Home
        home_topspeed = np.max(list(list(kpis.values())[0]['TopSpeedPlayer'].values()))
        home_topspeed_player = list(list(kpis.values())[0]['TopSpeedPlayer'].keys())[
            list(list(kpis.values())[0]['TopSpeedPlayer'].values()).index(home_topspeed)]
        self.update_team_speed('Home Speed', f'{home_topspeed_player}: {home_topspeed}')
        # TopSpeed Away
        away_topspeed = np.max(list(list(kpis.values())[1]['TopSpeedPlayer'].values()))
        away_topspeed_player = list(list(kpis.values())[1]['TopSpeedPlayer'].keys())[
            list(list(kpis.values())[1]['TopSpeedPlayer'].values()).index(away_topspeed)]
        self.update_team_speed('Away Speed', f'{away_topspeed_player}: {away_topspeed}')
        self.adjust_window_size()

        # All speeds
        self.home_topspeeds = list(kpis.values())[0]['TopSpeedPlayer']
        self.away_topspeeds = list(kpis.values())[1]['TopSpeedPlayer']

    def update_kpi_function(self):
        logging.basicConfig(level=logging.INFO)
        tf08_data, tf08_success = self.downloader.download_tf08_feed()
        self.update_feed_status('TF08', tf08_success)
        self.get_kpi_function(tf08_data)
        logging.info(f'The values for {self.game_id} have been updated')

    def create_speed_window(self, home_topspeeds, away_topspeeds):
        # Create a new Toplevel window
        self.speed_window = tk.Toplevel(self.root)
        self.speed_window.title("Player Top Speeds")

        # Create a Notebook (tabs)
        self.speed_notebook = ttk.Notebook(self.speed_window)
        self.speed_notebook.pack(expand=True, fill="both")

        # Create tabs for home and away speeds
        self.home_speed_frame = ttk.Frame(self.speed_notebook)
        self.away_speed_frame = ttk.Frame(self.speed_notebook)

        self.speed_notebook.add(self.home_speed_frame, text="Home Speeds")
        self.speed_notebook.add(self.away_speed_frame, text="Away Speeds")

        # Populate home speeds tab
        self.populate_speed_tab(self.home_speed_frame, home_topspeeds)

        # Populate away speeds tab
        self.populate_speed_tab(self.away_speed_frame, away_topspeeds)

    def populate_speed_tab(self, frame, topspeeds):
        # Create a DataFrame from the topspeeds dictionary
        df = pd.DataFrame(list(topspeeds.items()), columns=['Name', 'Speed'])

        # Sort DataFrame by Speed in descending order
        df = df.sort_values(by='Speed', ascending=False)

        # Format the DataFrame string with center-aligned names
        df_str = df.to_string(index=False)

        # Convert the DataFrame string to list of lines
        lines = df_str.split('\n')

        # Find the width of the 'Name' column to center-align the text
        name_width = df['Name'].str.len().max()

        # Center-align the 'Name' column
        centered_lines = [f"{line[:name_width].center(name_width)}  {line[name_width:].lstrip()}" for line in lines]

        # Join the centered lines back into a single string
        centered_df_str = '\n'.join(centered_lines)

        # Create a Text widget to display the centered DataFrame
        self.speed_text = tk.Text(frame, wrap=tk.WORD)

        # Insert centered DataFrame string into Text widget
        self.speed_text.insert(tk.END, centered_df_str)

        # Configure the text widget to fit the content width
        self.speed_text.configure(width=name_width + 10)

        # Pack the text widget
        self.speed_text.pack(padx=10, pady=10, fill="both", expand=True)

    def toggle_speed_window(self):
        if hasattr(self, 'speed_window') and self.speed_window:
            self.speed_window.destroy()
            del self.speed_window
        else:
            self.create_speed_window(self.home_topspeeds, self.away_topspeeds)

class TextHandler(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.insert(tk.END, msg + '\n')


class FootballDataProcessor:
    def __init__(self, game_id, vendor_id, protocol):
        self.data_queue = queue.Queue()
        self.game_id = game_id
        self.vendor_id = vendor_id
        self.protocol = protocol

    def fetch_data(self):
        while True:
            try:
                # Get temporary API key for live subscription
                tmp_url = f'https://api.tracab.com/api/internal/generatetempapikey'
                r_tmpkey = requests.get(tmp_url, headers=HEADERS)
                tmpkey = json.loads(r_tmpkey.content.decode('utf8'))['tempApiKey']

                # Define the JSON data for authentication
                auth_data = {
                    "TemporaryAPIKey": tmpkey,
                    "ClassID": "TCMDAuthenticationRequest",
                    "UserID": 360
                }

                # Convert JSON data to string
                json_message = json.dumps(auth_data)

                # Calculate the size of the JSON message
                message_size = len(json_message)

                # Convert the size to a 32-bit integer (4 bytes)
                size_bytes = struct.pack('!I', message_size)

                # Check connection with Heartbeat
                heartbeat_data = {
                    "ClassID": "TCMDClientHeartBeat",
                }
                # Convert JSON data to string
                heartbeat_message = json.dumps(heartbeat_data)

                # Calculate the size of the JSON message
                heartbeat_message_size = len(heartbeat_message)

                # Convert the size to a 32-bit integer (4 bytes)
                heartbeat_size_bytes = struct.pack('!I', heartbeat_message_size)

                # Send StartSubscription
                startsub_data = {
                    "GetLive": True,
                    "GameID": self.game_id,
                    "ClassID": "TCMDStartGameStreamSubscriptionRequest",
                    "VendorID": self.vendor_id,
                    "OutProtocol": self.protocol
                }
                # Convert JSON data to string
                startsub_message = json.dumps(startsub_data)

                # Calculate the size of the JSON message
                startsub_message_size = len(startsub_message)

                # Convert the size to a 32-bit integer (4 bytes)
                startsub_size_bytes = struct.pack('!I', startsub_message_size)

                # Define the host and port of the stream API
                host = 'stream-api.tracab.com'
                port = 37718

                # Establish a connection to the stream API and send a heartbeat
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((host, port))

                    # Send the size of the JSON message as a 32-bit integer
                    s.sendall(size_bytes)

                    # Send the JSON message
                    s.sendall(json_message.encode())

                    # Receive response if needed
                    response = s.recv(1024)

                    # Process response
                    print("Response:", response.decode())

                    # Send the size of the JSON message as a 34-bit integer
                    s.sendall(heartbeat_size_bytes)

                    # Send the JSON message
                    s.sendall(heartbeat_message.encode())

                    # Receive response if needed
                    heartbeat_response = s.recv(1024)

                    # Process response
                    print("Response:", heartbeat_response.decode('iso-8859-1'))

                    # Send the size of the JSON message as a 32-bit integer
                    s.sendall(startsub_size_bytes)

                    # Send the JSON message
                    s.sendall(startsub_message.encode())

                    # Receive response if needed
                    startsub_response = s.recv(1024)

                    # Process response
                    print("Response:", startsub_response.decode('iso-8859-1'))

                    print("Status ID is 1. Ready to receive data stream.")
                    # Receive and process data stream
                    s.settimeout(10)
                    while True:
                        try:
                            data = s.recv(1024)
                            self.data_queue.put(data)
                            if not data:
                                break
                            # Process the received data as needed
                            print("Received data:", data.decode())
                        except socket.timeout:
                            print("Timeout reached. Stopping receiving process.")
                            break

            except Exception as e:
                print(f"Error fetching data: {e}")
                time.sleep(10)

    def process_data(self):
        while True:
            try:
                # Get data from the queue
                data = self.data_queue.get()

                # Process the data (Replace with your data processing logic)
                # For example: print the data
                print(data)

                # Mark the data task as done
                self.data_queue.task_done()

            except Exception as e:
                print(f"Error processing data: {e}")
