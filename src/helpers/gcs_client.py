import os
from dataclasses import dataclass

from dotenv import load_dotenv
from google.cloud import storage

from helpers.utilities import load_pb_file_from_gcs

load_dotenv()


@dataclass
class BucketClient:
    bucket_name = "pabulib_files"

    def __post_init__(self):
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(self.bucket_name)

    def list_all_blobs(self):
        # List all blobs (files) in the bucket
        blobs = self.storage_client.list_blobs(self.bucket_name)

        # Print the name of each file in the bucket
        print(f"Files in bucket '{self.bucket_name}':")
        for blob in blobs:
            print(blob.name)

    def download_pb_file(self, file_name):
        # Get PB content

        blob = self.bucket.blob(file_name)
        file_content = blob.download_as_text(encoding="utf-8-sig")

        # Parse the custom pabulib format
        meta, projects, votes, votes_in_projects, scores_in_projects = (
            load_pb_file_from_gcs(file_content)
        )

        # Print or further process the parsed data
        print("Meta:", meta)
        # print("Projects:", projects)
        # print("Votes:", votes)

    def upload_pb_file(self, file_path):
        file_name = os.path.basename(file_path)
        blob = self.bucket.blob(file_name)
        blob.upload_from_filename(file_path)

        print(f"File {file_path} uploaded to {self.bucket_name}/{file_name}.")
