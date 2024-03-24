#############
## Imports ##
#############


import os
import pandas as pd
import zlib
import base64
import io
import json


###############
## Constants ##
###############


try:
    cwd = os.path.dirname(os.path.abspath(__file__))
except NameError as e:
    cwd = os.getcwd() 

data_directory = os.path.join(cwd, "data") 
appdata_directory = os.path.join(data_directory, "appdata")
reports_directory = os.path.join(data_directory, "reports")

###############
## Functions ##
###############

def get_ghg_report_name_df(ghg_report_directory):

    files = os.listdir(ghg_report_directory)
    data = []

    # Iterate over the files
    for file in files:
        # Extract country, account, and year from the file name
        parts = file.split("_")
        country = parts[0]
        account = parts[1]
        year = parts[-1].split(".")[0]

        # Append the extracted information to the data list
        data.append([file, country, account, year])

    # Create a DataFrame from the data list
    df = pd.DataFrame(data, columns=["file_name", "country", "account", "year"])

    # Display the DataFrame
    return df

def compress_df_to_string(df):
    # Convert DataFrame to bytes
    df_bytes = df.to_csv(index=False).encode()
    # Compress bytes using zlib
    compressed_bytes = zlib.compress(df_bytes)
    # Encode compressed bytes to base64 string
    compressed_string = base64.b64encode(compressed_bytes).decode()
    return compressed_string

def decompress_string_to_df(compressed_string):
    # Decode base64 string to compressed bytes
    compressed_bytes = base64.b64decode(compressed_string)
    # Decompress bytes using zlib
    decompressed_bytes = zlib.decompress(compressed_bytes)
    # Convert bytes to DataFrame
    df = pd.read_csv(io.BytesIO(decompressed_bytes))
    return df

def get_ghg_countries_accounts_df():
    return pd.read_csv(os.path.join(appdata_directory, "ghg_countries_accounts.csv"))

def get_contact_info_json():
    with open(os.path.join(appdata_directory,"contact_info.json"), "r") as fob:
        return json.loads(fob.read())
