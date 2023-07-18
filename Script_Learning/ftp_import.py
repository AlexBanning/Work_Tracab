from ftplib import FTP
import ftputil

# ftp = FTP(host="213.168.127.130", user="AlexTest", passwd="RobberyandLahm5%")

# ftp.retrlines('LIST')
# ftp.cwd('deltatre')
# ftp.retrlines('LIST')
# ftp.cwd('MatchInfo')
# ftp.retrlines('LIST')
# ftp.cwd('51')
# ftp.retrlines('LIST')
# ftp.cwd('2022')
# ftp.retrlines('LIST')
# ftp.cwd('schedule')
# ftp.retrlines('LIST')

# localfile = open(filename, 'wb')
# ftp.retrbinary(cmd='RETR ' + filename, callback=localfile.write)

# Different option to download files from FTP using FTPutil
# Need to test if it also works to simply open a file and read the xml-information without downloading it
server = "213.168.127.130"
user = "AlexTest"
password = "RobberyandLahm5%"
filename = 'schedule.xml'
f = open(filename, "w")
with ftputil.FTPHost(server, user, password) as ftp_host:
    ftp_host.chdir('deltatre/MatchInfo/51/2022/schedule')
    ftp_host.open(filename)
    if ftp_host.path.isfile(filename):
        ftp_host.download(filename, filename)


fifa_path = "FIFA/285026"


