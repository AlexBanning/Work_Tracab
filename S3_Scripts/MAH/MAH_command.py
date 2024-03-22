"""
Purpose of this code shall be to return the cmd-command to the user that is necessary to upload the videos to the MAH.
Additionally, it can also return the names for each video feed.

v0.1 2024/03/14 14:15
    - First version of a simple GUI that is used to generate the cmd-command and let the user copy it to the clipboard
v1.0 2024/03/22 15:00
    - Release version v1.0 that can generate the upload command and each individual feed name with a GUI, enabling the
      User to copy the names and command to the clipboard
"""

import sys
import os
import tkinter as tk
from tkinter import ttk
from MLS.MLS_Teams import MLS
from TracabModules.Internal.gamestats_functions import get_match_info
from TracabModules.Internal.server_manipulations import newest_folder, get_feed_names
from TracabModules.Internal.scheduleFunctions import get_STSID


def display_feed_names(sts_id, match):
    feed_names = get_feed_names(sts_id, match)  # Assuming this function returns four strings
    feed_names_window = tk.Toplevel(root)
    feed_names_window.title("Feed Names")
    feed_names_window.geometry("500x200")

    def copy_individual_feed_name(feed_name):
        root.clipboard_clear()
        root.clipboard_append(feed_name)

    for feed_name in feed_names:
        feed_name_frame = ttk.Frame(feed_names_window)
        feed_name_frame.pack(fill='x', padx=10, pady=5)

        feed_name_label = ttk.Label(feed_name_frame, text=feed_name, font=('Arial', 10))
        feed_name_label.pack(side='left')

        copy_feed_button = ttk.Button(feed_name_frame, text="Copy", command=lambda name=feed_name: copy_individual_feed_name(name))
        copy_feed_button.pack(side='right', padx=(10, 0))


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

    return sts_id, match


def copy_command():
    command = command_text.get("1.0", "end-1c")
    root.clipboard_clear()  # Clear the clipboard
    root.clipboard_append(command)  # Append command to clipboard


def display_feed_button_callback():
    sts_id, match = generate_command()
    display_feed_names(sts_id, match)


root = tk.Tk()
root.title("Upload Command Generator")
root.geometry("400x250")  # Set window size

style = ttk.Style()
style.configure("TButton", padding=6, relief="flat", background="#ccc", font=('Arial', 10))
style.configure("TFrame", background="grey64")

frame = ttk.Frame(root)
frame.pack(fill='both', expand=True)

generate_button = ttk.Button(frame, text="Generate Command", command=generate_command)
generate_button.pack(pady=10)

command_text = tk.Text(frame, height=5, width=40, font=('Arial', 10), bg='white')
command_text.pack(pady=10)

copy_button = ttk.Button(frame, text="Copy Command", command=copy_command)
copy_button.pack(pady=5)

# Adding a button to trigger display of feed names
display_feed_button = ttk.Button(frame, text="Display Feed Names", command=display_feed_button_callback)
display_feed_button.pack(pady=5)

root.mainloop()





