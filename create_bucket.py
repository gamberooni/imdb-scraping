from minio import Minio
from minio.error import S3Error
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

def main():
    # create client
    client = Minio(
        "localhost:9000",
        access_key="admin",
        secret_key="password",
        secure=False,
    )

    # specify bucket name
    bucket_name = "imdb"

    # create the bucket if not exists
    if client.bucket_exists(bucket_name):
        logging.info(f"Bucket '{bucket_name}' already exists.")
    else:
        client.make_bucket(bucket_name)
        logging.info(f"Created bucket '{bucket_name}'")

if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        logging.error("Error occured.", exc)
        