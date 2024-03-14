import os
import glob
import shutil
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk
import logging


def newest_folder(path):
    """
    Return the newest folder of all folders within a directory
    :param path: filepath as str
    :return:
        str: filepath of newest folder
    """
    folders = [a for a in os.listdir(path) if
               os.path.isdir(os.path.join(path, a))]
    paths = [os.path.join(path, basename) for basename in folders]
    return max(paths, key=os.path.getctime)


def newest_file(path, format):
    """
    Return the newest file inside a folder
    :param path: filepath as str
    :param format: str
        String that indicates the format of the requested file
    :return:
        str: filepath of newest file
    """
    list_of_files = glob.glob(path + '/*.' + format)
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


def choose_file(initialdir, feed, allowed_types):
    file = filedialog.askopenfilename(
        initialdir=initialdir,
        title=feed,
        filetypes=[allowed_types]
    )
    return file


def move_videos(sts_id, match, date, filepath_new):
    """

    :return:
    """
    # Create dictionary for video feeds
    feeds = {'1': 'TacticalFeed.mp4', '2': 'PanoramicFeed.mp4', '3': 'HighBehind_2.mp4',
             '4': 'HighBehind_1.mp4'}

    # Loop, that goes through all four feeds to move and rename them
    for feed, i in enumerate(feeds):
        print(feeds[i])
        filename_new = sts_id + '_' + match + '_' + feeds[i]
        if feeds[i] == 'TacticalFeed.mp4':
            os.chdir(r'\\192.168.7.75\d\TraCamVideoAndSetupXML' + '\\' + date)
            for file in glob.glob("*.mp4"):
                print(filepath_new + '\\' + filename_new)
                shutil.copy(file, filepath_new + '\\' + filename_new)
        if feeds[i] == 'PanoramicFeed.mp4':
            os.chdir(r'\\192.168.7.74\d\TraCamVideoAndSetupXML' + '\\' + date)
            for file in glob.glob("*.mp4"):
                print(filepath_new + '\\' + filename_new)
                shutil.copy(file, filepath_new + '\\' + filename_new)
        elif feeds[i] == 'HighBehind_1.mp4' or feeds[i] == 'HighBehind_2.mp4':
            os.chdir(r'\\192.168.7.76\d\TraCamVideoAndSetupXML' + '\\' + date)
            for file in glob.glob("*.mp4"):
                if feeds[i] == 'HighBehind_2.mp4' and 'PanoB' in file:
                    print(filepath_new + '\\' + filename_new)
                    shutil.copy(file, filepath_new + '\\' + filename_new)
                elif feeds[i] == 'HighBehind_1.mp4' and 'PanoD' in file:
                    print(filepath_new + '\\' + filename_new)
                    shutil.copy(file, filepath_new + '\\' + filename_new)

    print('All files have been copied and renamed')


def display_popup(title, message):
    """

    :param title:
    :param message:
    :return:
    """
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title=title, message=message)
    root.mainloop()


def rename_htf_files(source_path, destination_path, new_filename):
    try:
        logging.info(f"Renaming {source_path} to {destination_path}\\{new_filename}")
        os.rename(source_path, f"{destination_path}\\{new_filename}")
    except FileNotFoundError:
        logging.error(f"File not found: {source_path}")
    except Exception as e:
        logging.error(f"Error renaming file: {e}")


def move_and_rename_feed(feed_type, feed_identifier, filepath_new, sts_id, match, date):
    def get_source_folder(feed_type, date):
        # Define your logic to determine the source folder based on feed_type
        if feed_type == 'TacticalFeed.mp4':
            return r'\\192.168.7.75\d\TraCamVideoAndSetupXML' + '\\' + date
        elif feed_type == 'PanoramicFeed.mp4':
            return r'\\192.168.7.74\d\TraCamVideoAndSetupXML' + '\\' + date
        elif feed_type == 'HighBehind_1.mp4' or feed_type == 'HighBehind_2.mp4':
            return r'\\192.168.7.76\d\TraCamVideoAndSetupXML' + '\\' + date
        else:
            # Handle other cases if needed
            return None

    feeds = {'AutoCam': 'TacticalFeed.mp4', 'PanoA': 'PanoramicFeed.mp4', 'PanoB': 'HighBehind_2.mp4',
             'PanoD': 'HighBehind_1.mp4'}

    source_folder = get_source_folder(feed_type,
                                      date)  # Define your function to get the source folder based on feed_type

    os.chdir(source_folder)

    for file in glob.glob("*.mp4"):
        new_filepath = os.path.join(filepath_new, f"{sts_id}_{match}_{feeds[str(feed_identifier)]}")

        if (feed_type == 'HighBehind_1.mp4' and f'{feed_identifier}' in file
                or feed_type == 'HighBehind_2.mp4' and f'{feed_identifier}' in file):
            print(f'{feed_type} copied to: {new_filepath} \n')
            shutil.copy(file, new_filepath)
        else:
            print(f'{feed_type} copied to: {new_filepath} \n')
            shutil.copy(file, new_filepath)
