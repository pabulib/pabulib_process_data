import csv
import io

from dotenv import load_dotenv

load_dotenv()

from google.cloud import storage

from helpers.utilities import load_pb_file_from_gcs


def main():
    bucket_name = "pabulib_files"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # List all blobs (files) in the bucket
    blobs = storage_client.list_blobs(bucket_name)

    # Print the name of each file in the bucket
    print(f"Files in bucket '{bucket_name}':")
    for blob in blobs:
        print(blob.name)

    # Get PB content
    file_name = "Poland_Częstochowa_2024_.pb"
    blob = bucket.blob(file_name)
    file_content = blob.download_as_text(encoding="utf-8-sig")

    # Parse the custom pabulib format
    meta, projects, votes, votes_in_projects, scores_in_projects = (
        load_pb_file_from_gcs(file_content)
    )

    # Print or further process the parsed data
    print("Meta:", meta)
    # print("Projects:", projects)
    # print("Votes:", votes)


if __name__ == "__main__":
    main()
