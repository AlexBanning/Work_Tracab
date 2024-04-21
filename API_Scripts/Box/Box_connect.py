from boxsdk import JWTAuth, Client
from boxsdk.exception import BoxAPIException

config = JWTAuth.from_settings_file('box_config.json')

# Create a Box client
client = Client(config)

# Create a Box client
client = Client(config)

try:
    # Get the root folder
    root_folder = client.folder(folder_id='0')  # '0' is the ID for the root folder

    # Get items in the root folder
    items = root_folder.get_items()

    # Print the names of items in the root folder
    for item in items:
        print(item.name)

except BoxAPIException as e:
    print(f"Box API Error: {e}")
