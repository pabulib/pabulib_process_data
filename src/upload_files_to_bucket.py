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

# all_blobs = client.get_all_blobs()
# for blob in all_blobs:
#     print(blob.name)
#     raise RuntimeError
