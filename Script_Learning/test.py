from speedtest import Speedtest

internet = Speedtest()

download_speed = internet.download()
upload_speed = internet.upload()

print("Download \t:", download_speed)
print("Upload   \t:", upload_speed)
