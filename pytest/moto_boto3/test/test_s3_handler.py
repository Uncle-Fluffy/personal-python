import boto3
from moto import mock_s3
from s3_handler import S3Handler

@mock_s3
def test_upload_s3_file():
    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket="my_bucket")
    s3_handler = S3Handler()
    s3_handler.upload_s3_file()
