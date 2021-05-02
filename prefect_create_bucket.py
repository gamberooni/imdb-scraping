from minio import Minio
from minio.error import S3Error
from conf import MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, BUCKET_NAME
from prefect import task, Flow
import prefect


@task
def create_bucket(bucket_name):
    logger = prefect.context.get("logger")
    
    client = Minio(
        MINIO_URL,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )

    try:
        # create the bucket if not exists
        if client.bucket_exists(bucket_name):
            logger.info(f"Bucket '{bucket_name}' already exists.")
            logger.info("Not creating new bucket.")
        else:
            client.make_bucket(bucket_name)
            logger.info(f"Created bucket '{bucket_name}'")
    except S3Error as exc:
        logger.error("Error occured.", exc)


def main():

    with Flow("create_bucket") as flow:
        create_bucket(BUCKET_NAME)

    flow.register("imdb-scraping")
    # flow.run()

if __name__ == "__main__":
    main()
        