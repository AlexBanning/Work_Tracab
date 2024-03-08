import ftputil

server = "213.168.127.130"
user = "Alex_Test"
password = "RobberyandLahm5%"


filename = 'renameHTF_bl2.exe'
ftp_dir = 'TRACAB_NEU/07_QC/Alex/Scripts/HTFs'

with ftputil.FTPHost(server, user, password) as ftp_host:
    ftp_host.chdir(ftp_dir)
    ftp_host.open(filename)
    if ftp_host.path.isfile(filename):
        ftp_host.download(filename, filename)