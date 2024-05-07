import pandas as pd
import requests
import logging
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import sys, os


BL1 = [
    "FC Bayern München",
    "RB Leipzig",
    "Borussia Dortmund",
    "Borussia Mönchengladbach",
    "Bayer 04 Leverkusen",
    "VfL Wolfsburg",
    "Eintracht Frankfurt",
    "1. FC Union Berlin",
    "1. FC Köln",
    "1. FC Heidenheim 1846",
    "TSG Hoffenheim",
    "FC Augsburg",
    "Sport-Club Freiburg",
    "VfB Stuttgart",
    "SV Darmstadt 98",
    "1. FSV Mainz 05",
    "VfL Bochum 1848",
    "SV Werder Bremen"
]


BL2 = [
    "FC St. Pauli",
    "Holstein Kiel",
    "Karlsruher SC",
    "Hamburger SV",
    "SpVgg Greuther Fürth",
    "SV Elversberg",
    "SV Wehen Wiesbaden",
    "1. FC Magdeburg",
    "VfL Osnabrück",
    "1. FC Nürnberg",
    "F.C. Hansa Rostock",
    "FC Schalke 04",
    "1. FC Kaiserslautern",
    "Hannover 96",
    "SC Paderborn 07",
    "Hertha BSC",
    "Eintracht Braunschweig",
    "Fortuna Düsseldorf"
]
class DataHub:
    def __init__(self):
        self.client_id = 'ChyronHego-2fac-9065-53ed'

    def season_id(self):
        logging.basicConfig(level=logging.INFO)
        url=(
            f'https://httpget.distribution.production.datahub-sts.de/DeliveryPlatform/REST/PullOnce/{self.client_id}/'
            f'DFL-01.07-BaseData-Season')
        # Sending a GET request
        response = requests.get(url)
        if response.status_code != 200:
            return logging.info(f'Error: {response.status_code}: {response.reason}')
        else:
            xml_data = response.text
            # Parse XML data with BeautifulSoup
            soup = BeautifulSoup(xml_data, 'xml')
            current_season_id = [x['SeasonId'] for x in soup.find_all('Season') if x['Season'] == '2023/2024'][0]

            return current_season_id

    def sts_competition_id(self, tracab_id):
        logging.basicConfig(level=logging.INFO)
        url=(
            f'https://httpget.distribution.production.datahub-sts.de/DeliveryPlatform/REST/PullOnce/{self.client_id}/'
            f'DFL-01.01-BaseData-Competition')
        # Sending a GET request
        response = requests.get(url)
        if response.status_code != 200:
            return logging.info(f'Error: {response.status_code}: {response.reason}')
        else:
            xml_data = response.text
            # Parse XML data with BeautifulSoup
            soup = BeautifulSoup(xml_data, 'xml')
            comps = soup.find_all('Competitions')[0].contents
            comp_id = [x['CompetitionId'] for x in comps[1::2] if x['DlProviderId'] == tracab_id][0]

        return comp_id

    def matchday_ids(self, season_id, comp_id):
        logging.basicConfig(level=logging.INFO)
        url_md_id = (
            f'https://httpget.distribution.production.datahub-sts.de/DeliveryPlatform/REST/PullOnce/{self.client_id}/'
            f'DFL-01.06-BaseData-Schedule/{season_id}')
        response = requests.get(url_md_id)
        if response.status_code != 200:
            return logging.info(f'Error: {response.status_code}: {response.reason}')
        else:
            xml_data = response.text
            soup = BeautifulSoup(xml_data, 'xml')
            matchday_ids = {
                x['MatchDay']: {'MatchDayId': x['MatchDayId'],'Date': x['StartDate'][:10]}
                for x in soup.find_all('Fixtures')[0].contents[1::2]
                if x['CompetitionId'] == comp_id
                }

        return matchday_ids

    def positionalfeed(self, season_id, comp_id, matchday_id):
        logging.basicConfig(level=logging.INFO)
        url = (f'https://httpget.distribution.production.datahub-sts.de/DeliveryPlatform/REST/PullOnce/{self.client_id}/'
                    f'DFL-07.03.01-Ranglisten-Saison_Spieler_Positionsdaten/{season_id}_{comp_id}_{matchday_id}')
        response = requests.get(url)
        if response.status_code != 200:
            return logging.info(f'Error: {response.status_code}: {response.reason}')
        else:
            stats_xml_data = response.text
            soup = BeautifulSoup(stats_xml_data, 'xml')

            speeds = [x for x in soup.find_all('Ranking') if x['Type'] == 'MaximumSpeed'][0]

        return speeds


def get_dfl_highspeeds(league, home, away):
    logging.basicConfig(level=logging.INFO)

    # Get the path to the directory containing the executable
    exe_dir = getattr(sys, '_MEIPASS', os.getcwd())

    # Construct the path to the CSV files
    csv_path1 = os.path.join(exe_dir, 'speeds_BL1.csv')
    csv_path2 = os.path.join(exe_dir, 'speeds_BL2.csv')

    try:
        if league == '1.Bundesliga':
            data = pd.read_csv(csv_path1)
        elif league == '2.Bundesliga':
            data = pd.read_csv(csv_path2)
        else:
            raise ValueError("Invalid league selected")

        # Continue processing the data if loading is successful
        logging.info("Data loaded successfully")

    except FileNotFoundError as e:
        logging.error(f"File not found: {e.filename}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

    home_data = data[data['Team'] == home].drop(columns=data.columns[[0,3]]).sort_values(by='Speed', ascending=False)
    away_data = data[data['Team'] == away].drop(columns=data.columns[[0,3]]).sort_values(by='Speed', ascending=False)
    top_ten = data.head(10).drop(columns=data.columns[[0,3]]).sort_values(by='Speed', ascending=False)

    return home_data, away_data, top_ten


class HighSpeedGUI:
    def __init__(self):
        self.leagues = ['1.Bundesliga', '2.Bundesliga']
        self.teams = {
            '1.Bundesliga': BL1,
            '2.Bundesliga': BL2
        }

        self.root = tk.Tk()
        self.root.title("Highspeed Fetcher")
        # Load Tracab Icon
        exe_dir = getattr(sys, '_MEIPASS', os.getcwd())
        self.root.iconbitmap(os.path.join(exe_dir, "Tracab.ico"))
        # Set Background colour
        self.root.configure(bg='#2F4F4F')

        # Adjust the size of the GUI window
        self.root.geometry("700x250")

        # Create a frame to contain the labels and buttons
        self.center_frame = tk.Frame(self.root)
        self.center_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.center_frame.configure(bg='#2F4F4F')

        # Configure row and column weights for center_frame
        self.center_frame.grid_rowconfigure(0, weight=1)
        self.center_frame.grid_columnconfigure(0, weight=1)

        # Dropdown list for selecting the league
        tk.Label(self.center_frame, text="Select League:", fg="#98FB98", bg="#2F4F4F").grid(row=0, column=0, padx=5, pady=2,
                                                                                        sticky="nw")
        self.league_var = tk.StringVar(self.root)
        self.league_dropdown = ttk.Combobox(self.center_frame, textvariable=self.league_var, values=self.leagues, state='readonly')
        self.league_dropdown.grid(row=0, column=1, padx=5, pady=2, sticky="nw")

        # Dropdown lists for selecting home and away teams
        tk.Label(self.center_frame, text="Home Team:", fg="#98FB98", bg="#2F4F4F").grid(row=1, column=0, padx=5, pady=2,
                                                                                        sticky="nw")
        self.home_team_var = tk.StringVar(self.root)
        self.home_team_dropdown = ttk.Combobox(self.center_frame, textvariable=self.home_team_var, values=[])
        self.home_team_dropdown.grid(row=1, column=1, padx=5, pady=2, sticky="nw")

        tk.Label(self.center_frame, text="Away Team:", fg="#98FB98", bg="#2F4F4F").grid(row=2, column=0, padx=5, pady=2,
                                                                                        sticky="nw")
        self.away_team_var = tk.StringVar(self.root)
        self.away_team_dropdown = ttk.Combobox(self.center_frame, textvariable=self.away_team_var, values=[])
        self.away_team_dropdown.grid(row=2, column=1, padx=5, pady=2, sticky="nw")

        # Button to fetch highspeed dataframes
        self.fetch_button = tk.Button(self.center_frame, text="Fetch Highspeeds", command=self.fetch_highspeeds)
        self.fetch_button.grid(row=3, column=0, columnspan=2, pady=0, sticky="nw")

        # Dataframes to display highspeeds
        self.home_df_text = tk.Text(self.center_frame, wrap=tk.WORD, height=10, width=35, relief='flat')
        self.home_df_text.grid(row=1, column=2, padx=(5,0), pady=0, sticky="nsew", columnspan=2)
        self.home_df_text.config(state=tk.DISABLED, fg="#98FB98" , bg=self.root.cget("bg"))
        self.home_df_text.grid_remove()

        # Vertical Scrollbar for home_df_text
        self.home_scrollbar = ttk.Scrollbar(self.center_frame, orient="vertical", command=self.home_df_text.yview)
        self.home_scrollbar.grid(row=1, column=4, pady=(0), sticky="nse")
        self.home_df_text.config(yscrollcommand=self.home_scrollbar.set)
        self.home_scrollbar.grid_remove()  # Hide the scrollbar initially

        self.away_df_text = tk.Text(self.center_frame, wrap=tk.WORD, height=10, width=35, relief='flat')
        self.away_df_text.grid(row=1, column=4, padx=0, pady=0, sticky="nsew", columnspan=2)
        self.away_df_text.config(state=tk.DISABLED, fg="#98FB98" , bg=self.root.cget("bg"))
        self.away_df_text.grid_remove()

        # Vertical Scrollbar for away_df_text
        self.away_scrollbar = ttk.Scrollbar(self.center_frame, orient="vertical", command=self.away_df_text.yview)
        self.away_scrollbar.grid(row=1, column=7, pady=(0, 2), sticky="nse")
        self.away_df_text.config(yscrollcommand=self.away_scrollbar.set)

        # Configure scrollbar style to match background color
        self.away_scrollbar.grid_remove()  # Hide the scrollbar initially

        # Adjust the window geometry
        self.adjust_window_size()

        self.league_dropdown.bind("<<ComboboxSelected>>", self.update_team_dropdowns)
        self.root.mainloop()

    def update_team_dropdowns(self, event):
        selected_league = self.league_var.get()
        teams_for_selected_league = self.teams.get(selected_league, [])
        self.home_team_dropdown.config(values=teams_for_selected_league)
        self.away_team_dropdown.config(values=teams_for_selected_league)

    def fetch_highspeeds(self):
        league = self.league_var.get()
        home_team = self.home_team_var.get()
        away_team = self.away_team_var.get()

        # Replace with your function to fetch highspeed dataframes based on home_team and away_team
        try:
            home_df, away_df, top_ten = get_dfl_highspeeds(league, home_team, away_team)
        except FileNotFoundError as e:
            error_msg = f"File not found: {e.filename}"
            logging.error(error_msg)
            messagebox.showerror("Error", error_msg)

        except Exception as e:
            error_msg = f"An error occurred: {e}"
            logging.error(error_msg)
            messagebox.showerror("Error", error_msg)
        # home_df = bayern_df
        # away_df = leverkusen_df

        if home_df is not None and away_df is not None:
            # Display highspeed dataframes in the text widgets
            self.display_dataframe(home_df, self.home_df_text)
            self.display_dataframe(away_df, self.away_df_text)

            # Update headers
            self.update_headers(home_team, away_team)

            # Show the text widgets
            self.home_df_text.grid()
            self.away_df_text.grid()
            # Adjust the window geometry
            self.adjust_window_size()

    def display_dataframe(self, df, text_widget):
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, df.to_string(index=False))
        text_widget.config(state=tk.DISABLED)

    def adjust_window_size(self):
        self.root.update_idletasks()  # Update the GUI to finish arranging widgets
        width = self.root.winfo_reqwidth()  # Get the required width of the GUI
        height = self.root.winfo_reqheight()  # Get the required height of the GUI
        self.root.geometry(f"{width}x{height}")  # Set the GUI window size

    def update_headers(self, home_team, away_team):
        bold_font = tkfont.Font(weight='bold')
        self.home_df_text_header = tk.Label(self.center_frame, text=home_team, font=bold_font, fg="white", bg="#2F4F4F",
                                            anchor='center')
        self.home_df_text_header.grid(row=0, column=2, padx=5, pady=(0,5), sticky="nsew")

        self.away_df_text_header = tk.Label(self.center_frame, text=away_team, font=bold_font, fg="white", bg="#2F4F4F",
                                            anchor='center')
        self.away_df_text_header.grid(row=0, column=4, padx=5, pady=(0,5), sticky="nsew")
