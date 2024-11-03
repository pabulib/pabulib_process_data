from helpers.gcs_client import BucketClient

client = BucketClient()

# List all blobs (PB files)
# client.list_all_blobs()

# Upload a blob (PB file)
file_path = ""
# client.upload_pb_file(file_path)

file_name = "Poland_Częstochowa_2024_.pb"
client.download_pb_file(file_name)
