"""
Purpose of this code shall be to return the cmd-command to the user that is necessary to upload the videos to the MAH.
Additionally, it can also return the names for each video feed.

v1.0 2024/03/14 14:15
    - First version of a simple GUI that is used to generate the cmd-command and let the user copy it to the clipboard
"""
import shutil
import sys
import os
import tkinter as tk
from tkinter import ttk
from MLS.MLS_Teams import MLS
from TracabModules.Internal.gamestats_functions import get_match_info
from TracabModules.Internal.server_manipulations import newest_folder, get_feed_names
from TracabModules.Internal.scheduleFunctions import get_STSID


def generate_command():
    match_folder = newest_folder(r'\\192.168.7.72\Rec')
    home, away, md, comp = get_match_info(match_folder)
    teams = MLS

    try:
        ht = teams[home]
    except KeyError:
        input('The home team cannot be found in the database. Please check with the developer.\n'
              'Please Insert the 3LC and Team Name!')
        ht = str(input())
        home = str(input())
        sys.exit()

    try:
        at = teams[away]
    except KeyError:
        input('The away team cannot be found in the database. Please check with the developer.\n'
              'Press Enter to leave!')
        at = str(input())
        away = str(input())
        sys.exit()

    match = str(ht) + '-' + str(at)
    sts_id, date = get_STSID(comp, home, away)
    filepath_new = os.getcwd() + '\\MD' + str(md) + '_' + match
    folder_new = str(sts_id) + '_' + match

    get_feed_names(sts_id, match)

    if comp == str(1):
        command = ('aws s3 cp "' + filepath_new +
                   '" "s3://mah-s3-download-section-mls-331812868623/Video/2024/MLSRegularSeason/Matchweek ' + md + '/'
                   + folder_new + '" --recursive')
    elif comp == str(100):
        command = ('aws s3 cp "' + filepath_new +
                   '" "s3://mah-s3-download-section-mls-331812868623/Video/2024/MLSRehearsals/' + md + '/'
                   + folder_new + '" --recursive')

    command_text.delete("1.0", "end")  # Clear previous text
    command_text.insert("1.0", command)  # Insert new command


def copy_command():
    command = command_text.get("1.0", "end-1c")
    root.clipboard_clear()  # Clear the clipboard
    root.clipboard_append(command)  # Append command to clipboard


root = tk.Tk()
root.title("Upload Command Generator")
root.geometry("600x300")  # Set window size

style = ttk.Style()
style.configure("TButton", padding=6, relief="flat", background="#ccc", font=('Arial', 10))
style.configure("TFrame", background="grey64")

frame = ttk.Frame(root)
frame.pack(fill='both', expand=True)

generate_button = ttk.Button(frame, text="Generate Command", command=generate_command)
generate_button.pack(pady=10)

command_text = tk.Text(frame, height=10, width=60, font=('Arial', 10), bg='white')
command_text.pack(pady=10)

copy_button = ttk.Button(frame, text="Copy Command", command=copy_command)
copy_button.pack(pady=5)

root.mainloop()