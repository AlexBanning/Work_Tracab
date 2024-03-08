import os
import glob
import shutil


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
