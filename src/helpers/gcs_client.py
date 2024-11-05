import os
from dataclasses import dataclass

from google.cloud import storage

import helpers.utilities as utils

logger = utils.create_logger()


def load_gcp_credentials(PROD=False):
    if PROD:
        sa_key = "sa_viewer_key.json"
    else:
        sa_key = "sa_admin_key.json"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), sa_key)


@dataclass
class BucketClient:
    bucket_name: str = "pabulib_files"

    def __post_init__(self):
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(self.bucket_name)

    def get_all_blobs(self):
        return self.storage_client.list_blobs(self.bucket_name)

    def print_all_blobs(self):
        # List all blobs (files) in the bucket
        blobs = self.get_all_blobs()

        # Print the name of each file in the bucket
        print(f"Files in bucket '{self.bucket_name}':")
        for blob in blobs:
            print(blob.name)

    def download_pb_file(self, file_name, encoding="utf-8-sig"):
        # Get PB content

        blob = self.bucket.blob(file_name)
        file_content = blob.download_as_text(encoding=encoding)

        # Parse the custom pabulib format
        meta, projects, votes, votes_in_projects, scores_in_projects = (
            utils.load_pb_file_from_gcs(file_content)
        )

        # Print or further process the parsed data
        print("Meta:", meta)
        # print("Projects:", projects)
        # print("Votes:", votes)

    def upload_pb_file(self, file_path, ts):
        file_name = os.path.basename(file_path)
        blob_path = f"{ts}/{file_name}"
        blob = self.bucket.blob(blob_path)
        blob.upload_from_filename(file_path)

        logger.info(f"File {file_path} uploaded to {self.bucket_name}/{blob_path}.")
