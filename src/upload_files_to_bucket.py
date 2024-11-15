import glob
import os
import time

import helpers.utilities as utils
from helpers.gcs_client import BucketClient, load_gcp_credentials

load_gcp_credentials()

logger = utils.create_logger()

BUCKET_NAME = "pabulib_files"  # then process to "pabulib_webpage_files"
UPLOAD_DIR = "upload"

pabulib_dir = os.path.join(os.getcwd(), "src")
upload_files = os.path.join(pabulib_dir, "output", UPLOAD_DIR, "*.pb")

client = BucketClient(BUCKET_NAME)

# List all blobs (PB files)
# client.print_all_blobs()

# Download file from bucket
# file_name = "Worldwide_Stanford_2021-22_Cal_High_Library_PB_vote_knapsacks_clean.pb"
# client.download_pb_file(file_name)


def upload_pb_files():

    files = glob.glob(upload_files)
    # utils.human_sorting(files)

    current_timestamp = int(time.time())
    for idx, pb_file in enumerate(files):
        client.upload_pb_file(pb_file, current_timestamp)

    logger.info(f"Uploading finished. Processed `{idx+1}` files.")


upload_pb_files()


# Then copy only newest versions of files (where ts = max(ts)) to web_bucket
# and split files into 3 csvs


# Upload a blob (PB file)
# file_name = "Poland_Częstochowa_2024_.pb"
# pabulib_dir = os.path.join(os.getcwd(), "src")
# file_output_path = os.path.join(pabulib_dir, "output", file_name)

# client.upload_pb_file(file_output_path)

### GET ONLY NEWEST VERSIONS AND UPLOAD TO web_bucket

from collections import defaultdict

# Assuming `all_blobs` is a list of blobs you already have
# and each blob's `name` attribute is structured as 'timestamp/filename'


def get_latest_files(all_blobs):
    # Dictionary to store the latest blob for each unique filename
    latest_files = defaultdict(lambda: (None, None))  # {filename: (timestamp, blob)}

    for blob in all_blobs:
        # Split the blob name to get timestamp and filename
        file_timestamp, file_name = blob.name.split("/")

        # Check if we need to update the latest file for this filename
        if (
            latest_files[file_name][0] is None
            or file_timestamp > latest_files[file_name][0]
        ):
            latest_files[file_name] = (file_timestamp, blob)

    # Extract only the blob objects for the latest files
    result = [blob for _, blob in latest_files.values()]
    return result


# Get only newest version of files
# all_blobs = client.get_all_blobs()
# latest_files = get_latest_files(all_blobs)
# print(f"Number of latest files: {len(latest_files)}")
# print("Newest files for each unique filename:")
# for blob in latest_files:
#     if "netherlands_assen_2024_.pb" in blob.name:
#         print(blob.name)
