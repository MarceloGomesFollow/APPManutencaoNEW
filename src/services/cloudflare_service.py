import boto3
from botocore.client import Config as ConfigClientR2
from ..config import Config


# Cliente S3 compatível com R2
s3 = boto3.client(
    's3',
    endpoint_url=Config.R2_ENDPOINT_URL,
    aws_access_key_id=Config.R2_ACCESS_KEY_ID,
    aws_secret_access_key=Config.R2_SECRET_ACCESS_KEY,
    config=ConfigClientR2(signature_version='s3v4'),
    region_name='auto'
)

def upload_file_to_r2(file, file_name):
    try:
        s3.upload_fileobj(file, Config.R2_BUCKET_NAME, file_name)
        return True
    except Exception as e:
        print(f"Erro ao enviar o arquivo para o R2: {e}")
        return False

def download_file_from_r2(file_name):
    try:
        obj = s3.get_object(Bucket=Config.R2_BUCKET_NAME, Key=file_name)
        return obj['Body'], obj['ContentType']
    except Exception as e:
        print(f"Erro ao baixar o arquivo do R2: {e}")
        return None, None
