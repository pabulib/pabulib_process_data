import os

from helpers.gcs_client import BucketClient, load_gcp_credentials

load_gcp_credentials()


bucket_name = "pabulib_files"
# bucket_name = "pabulib_webpage_files"
client = BucketClient(bucket_name)

# List all blobs (PB files)
client.list_all_blobs()

# Upload a blob (PB file)
file_name = "Poland_Częstochowa_2024_.pb"
pabulib_dir = os.path.join(os.getcwd(), "src")
file_output_path = os.path.join(pabulib_dir, "output", file_name)

# client.upload_pb_file(file_output_path)

# file_name = "Worldwide_Stanford_2021-22_Cal_High_Library_PB_vote_knapsacks_clean.pb"
# client.download_pb_file(file_name)
