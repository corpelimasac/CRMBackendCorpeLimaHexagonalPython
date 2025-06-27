import boto3
import os

def upload_file_to_s3(local_path, s3_key, bucket, region):
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=region
    )
    s3.upload_file(local_path, bucket, s3_key, ExtraArgs={'ACL': 'public-read'})
    url = f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
    return url