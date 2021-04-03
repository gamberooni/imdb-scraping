from minio import Minio
from minio.error import S3Error


def main():
    # create client
    client = Minio(
        "localhost:9000",
        access_key="admin",
        secret_key="password",
        secure=False,
    )

    # make bucket
    bucket_name = "imdb"

    # create the bucket if not exists
    if client.bucket_exists(bucket_name):
        print(f"Bucket '{bucket_name}' already exists.")
    else:
        client.make_bucket(bucket_name)
        print(f"Created bucket '{bucket_name}'")

if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        print("Error occured.", exc)
        