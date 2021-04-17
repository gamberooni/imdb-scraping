from minio import Minio
from minio.error import S3Error
import logging
from conf import MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, BUCKET_NAME

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

def main():
    # create client
    client = Minio(
        MINIO_URL,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )

    # specify bucket name
    bucket_name = BUCKET_NAME

    # create the bucket if not exists
    if client.bucket_exists(bucket_name):
        logging.info(f"Bucket '{bucket_name}' already exists.")
        logging.info("Not creating new bucket.")
    else:
        client.make_bucket(bucket_name)
        logging.info(f"Created bucket '{bucket_name}'")

if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        logging.error("Error occured.", exc)
        