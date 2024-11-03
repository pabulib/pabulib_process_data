import os

from helpers.gcs_client import BucketClient

bucket_name = "pabulib_files"
client = BucketClient(bucket_name)

# List all blobs (PB files)
client.list_all_blobs()

# Upload a blob (PB file)
file_name = "Worldwide_Stanford_2022_Jersey_City_Ward_E_vote_knapsacks_clean.pb"
pabulib_dir = os.path.join(os.getcwd(), "src")
file_output_path = os.path.join(pabulib_dir, "output", file_name)

client.upload_pb_file(file_output_path)

# file_name = "Worldwide_Stanford_2021-22_Cal_High_Library_PB_vote_knapsacks_clean.pb"
# client.download_pb_file(file_name)
