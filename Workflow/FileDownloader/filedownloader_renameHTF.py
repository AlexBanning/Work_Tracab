import ftputil

server = "213.168.127.130"
user = "Alex_Test"
password = "RobberyandLahm5%"

choice = input('For which league do you want to update the software? \n'
               '1: BL1 \n'
               '2: BL2 \n')

filenames_bl2 = ['renameHTF_bl2.exe', 'BL2_HTF_Schedule.xlsx']
filenames_bl1 = ['renameHTF_bl1.exe', 'BL1_HTF_Schedule.xlsx']

ftp_dir = 'TRACAB_NEU/07_QC/Alex/Scripts/HTFs'
if choice == str(1):
    for filename in filenames_bl1:
        try:
            with ftputil.FTPHost(server, user, password) as ftp_host:
                ftp_host.chdir(ftp_dir)
                ftp_host.open(filename)
                if ftp_host.path.isfile(filename):
                    ftp_host.download(filename, filename)
        except:
            pass
elif choice == str(2):
    for filename in filenames_bl2:
        try:
            with ftputil.FTPHost(server, user, password) as ftp_host:
                ftp_host.chdir(ftp_dir)
                ftp_host.open(filename)
                if ftp_host.path.isfile(filename):
                    ftp_host.download(filename, filename)
        except:
            pass