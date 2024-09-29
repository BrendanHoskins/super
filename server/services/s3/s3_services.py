import boto3
import os

FILES_TO_EXTRACT_INSIGHTS_FROM_S3_BUCKET_NAME = os.getenv("FILES_TO_EXTRACT_INSIGHTS_FROM_S3_BUCKET_NAME")
S3_USER_ACCESS_KEY = os.getenv("S3_USER_ACCESS_KEY")
S3_USER_SECRET_ACCESS_KEY = os.getenv("S3_USER_SECRET_ACCESS_KEY")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_FOLDER_WITH_TXT_VERSIONS_OF_EVERY_USER_UPLOADED_FILE = os.getenv("S3_FOLDER_WITH_TXT_VERSIONS_OF_EVERY_USER_UPLOADED_FILE")

def upload_file_to_s3(file, bucket_name, file_key):
    s3 = boto3.client('s3', aws_access_key_id=os.getenv('S3_USER_ACCESS_KEY'), aws_secret_access_key=os.getenv('S3_USER_SECRET_ACCESS_KEY'))
    s3.upload_fileobj(file, bucket_name, file_key)

def delete_file_from_s3(bucket_name, file_key):
    s3 = boto3.client('s3', aws_access_key_id=S3_USER_ACCESS_KEY, aws_secret_access_key=S3_USER_SECRET_ACCESS_KEY)
    try:
        s3.delete_object(Bucket=bucket_name, Key=file_key)
        print(f"File {file_key} deleted from S3 bucket {bucket_name}")
    except Exception as e:
        print(f"Error deleting file from S3: {e}")