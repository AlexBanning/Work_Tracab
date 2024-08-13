import os
import glob
import shutil
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk
import logging
import ftputil


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
    :param path: filepath as string
    :param format: string
        String that indicates the format of the requested file
    :return:
        str: filepath of newest file
    """
    list_of_files = glob.glob(path + '/*.' + format)
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


def choose_file(initialdir, title, allowed_types, keyword=None):
    root = tk.Tk()
    root.withdraw()

    while True:
        file_path = filedialog.askopenfilename(
            parent=root,
            initialdir=initialdir,
            title=title,
            filetypes=[allowed_types]
        )
        if not file_path:
            root.destroy()
            return None  # User canceled the dialog

        if keyword and keyword not in file_path:
            messagebox.showwarning('Invalid File Selected', f'Please select a {title} feed!')
        else:
            root.destroy()
            return file_path


def display_popup(title, message):
    """

    :param title:
    :param message:
    :return:
    """
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title=title, message=message)
    #root.mainloop()


def rename_htf_files(source_path, destination_path, new_filename):
    try:
        logging.info(f"Renaming {source_path} to {destination_path}\\{new_filename}")
        os.rename(source_path, f"{destination_path}\\{new_filename}")
        display_popup("Renaming HTFs", f"{new_filename} has been successfully renamed!")
    except FileNotFoundError:
        logging.error(f"File not found: {source_path}")
        display_popup("Renaming HTFs", f"File not found: {source_path}")
    except Exception as e:
        logging.error(f"Error renaming file: {e}")
        display_popup("Renaming HTFs", f"Error renaming file: {e}")


def get_source_folder(feed_type, date, mobile=False, nsh=False):
    folder_map = {
        'TacticalFeed.mp4': r'\\192.168.7.75\d\TraCamVideoAndSetupXML' + '\\' + date,
        'PanoramicFeed.mp4': r'\\192.168.7.74\d\TraCamVideoAndSetupXML' + '\\' + date,
        'HighBehind_1.mp4': r'\\192.168.7.76\d\TraCamVideoAndSetupXML' + '\\' + date,
        'HighBehind_2.mp4': r'\\192.168.7.76\d\TraCamVideoAndSetupXML' + '\\' + date
    }

    if mobile:
        folder_map = {
            'TacticalFeed.mp4': r'D:\\AL',
            'PanoramicFeed.mp4': r'D:\\AL'
        }

    if nsh:
        folder_map = {
            'TacticalFeed.mp4': r'D:\\TraCamVideoAndSetupXML' + '\\' + date,
            'PanoramicFeed.mp4': r'\\192.168.7.74\d\TraCamVideoAndSetupXML' + '\\' + date,
            'HighBehind_1.mp4': r'\\192.168.7.76\d\TraCamVideoAndSetupXML' + '\\' + date,
            'HighBehind_2.mp4': r'\\192.168.7.76\d\TraCamVideoAndSetupXML' + '\\' + date
        }

    return folder_map.get(feed_type)


def copy_files(filepath_new, sts_id, match, feed_type, date, mobile=False):
    if mobile:
        for file in glob.glob("*.mp4"):
            if feed_type == 'PanoramicFeed.mp4':
                if 'PanoA' in file and date in file:
                    new_filepath = os.path.join(filepath_new, f"{sts_id}_{match}_{feed_type}")
                    shutil.copy(file, new_filepath)
                    print(f'{feed_type} copied to: {new_filepath}')
            elif feed_type == 'TacticalFeed.mp4':
                if 'AutoCam' in file and date in file:
                    new_filepath = os.path.join(filepath_new, f"{sts_id}_{match}_{feed_type}")
                    shutil.copy(file, new_filepath)
                    print(f'{feed_type} copied to: {new_filepath}')

    else:
        for file in glob.glob("*.mp4"):
            if feed_type == 'HighBehind_1.mp4':
                if 'PanoD' in file:
                    new_filepath = os.path.join(filepath_new, f"{sts_id}_{match}_{feed_type}")
                    print(f'{feed_type} copied to: {new_filepath}')
                    shutil.copy(file, new_filepath)
            elif feed_type == 'HighBehind_2.mp4':
                if 'PanoB' in file:
                    new_filepath = os.path.join(filepath_new, f"{sts_id}_{match}_{feed_type}")
                    print(f'{feed_type} copied to: {new_filepath}')
                    shutil.copy(file, new_filepath)
            elif feed_type == 'PanoramicFeed.mp4':
                if 'PanoA' in file:
                    new_filepath = os.path.join(filepath_new, f"{sts_id}_{match}_{feed_type}")
                    print(f'{feed_type} copied to: {new_filepath}')
                    shutil.copy(file, new_filepath)
            else:
                new_filepath = os.path.join(filepath_new, f"{sts_id}_{match}_{feed_type}")
                print(f'{feed_type} copied to: {new_filepath}')
                shutil.copy(file, new_filepath)


def move_and_rename_feed(filepath_new, sts_id, match, date, mobile=False, nsh=False):
    if mobile:
        feeds = {'AutoCam': 'TacticalFeed.mp4', 'PanoA': 'PanoramicFeed.mp4'}
    else:
        feeds = {'AutoCam': 'TacticalFeed.mp4', 'PanoA': 'PanoramicFeed.mp4', 'PanoB': 'HighBehind_2.mp4',
                 'PanoD': 'HighBehind_1.mp4'}

    print(f'Starting copying process \n')
    for feed_identifier, feed_type in feeds.items():
        source_folder = get_source_folder(feed_type, date, mobile, nsh)
        if source_folder:
            os.chdir(source_folder)
            copy_files(filepath_new, sts_id, match, feed_type, date=date, mobile=mobile)
        else:
            print(f"No source folder found for feed type: {feed_type}")


def get_feed_names(sts_id, match, mobile=False):
    """

    :param sts_id:
    :param match:
    :return:
    """

    if mobile:
        feeds = {'AutoCam': 'TacticalFeed', 'PanoA': 'PanoramicFeed'}
    else:
        feeds = {'AutoCam': 'TacticalFeed', 'PanoA': 'PanoramicFeed', 'PanoB': 'HighBehind_2',
                 'PanoD': 'HighBehind_1'}

    feed_names = []
    for feed_identifier, feed_type in feeds.items():
        new_filename = f'{sts_id}_{match}_{feeds[str(feed_identifier)]}'
        feed_names.append(new_filename)

    return feed_names


def filedownloader(filename, source, destination):
    """

    :param filename:
    :param source:
    :param destination:
    :return:
    """

    server = "213.168.127.130"
    user = "Alex_Test"
    password = "RobberyandLahm5%"

    try:
        with ftputil.FTPHost(server, user, password) as ftp_host:
            ftp_host.chdir(source)
            ftp_host.open(filename)
            if ftp_host.path.isfile(filename):
                ftp_host.download(filename, destination + filename)
                print(f'{filename} has been downloaded to {destination}')
    except:
        pass
