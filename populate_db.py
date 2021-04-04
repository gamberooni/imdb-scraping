from minio import Minio
import json
import io
import re


client = Minio(
    "localhost:9000",
    access_key="admin",
    secret_key="password",
    secure=False,
)

BUCKET_NAME = "imdb"
found = client.bucket_exists(BUCKET_NAME)
if found:
    print(f"Bucket '{BUCKET_NAME}' exists. Proceeding job.")
else:
    raise Exception(f"Bucket '{BUCKET_NAME}' does not exist. Aborting...")

FILE_PREFIX = "2021-04-04/"
objects = client.list_objects(bucket_name=BUCKET_NAME, prefix=FILE_PREFIX)

# def get_obj_filepaths(objects):
#     '''
#     Parameters
#     ----------
#     objects: MinIO Object
#         An iterator of Objects stored in MinIO Bucket
#     '''
#     filepaths = []
#     for obj in objects:
#     # {'_bucket_name': 'data', '_object_name': 'imdb/2021-04-03/anime_1.json', 
#     #   '_last_modified': datetime.datetime(2021, 3, 18, 1, 42, 59, 439000, tzinfo=datetime.timezone.utc), 
#     #   '_etag': '85951813368733551d7c8ada22923374', '_size': 118618497, '_metadata': {}, '_version_id': None, 
#     #   '_is_latest': None, '_storage_class': 'STANDARD', '_owner_id': '', '_owner_name': '', '_content_type': None}
#         if obj.object_name.split('.')[-1] == "json":
#             filepaths.append(f"{obj.bucket_name}/{obj.object_name}")  
#     return filepaths 

# filepaths = get_obj_filepaths(objects)
# print(filepaths)
for obj in objects:
    o = client.get_object(BUCKET_NAME, obj.object_name)
    data = json.load(io.BytesIO(o.data))
    data_dict = json.loads(data)
    print(data_dict[0])
    print(data_dict[0].keys())
    print(data_dict[0]["summary_text"])
    # for d in data_dict:
    #     print(d.keys())
    #     print("\n")
    # print(json.dumps(data, indent=4, sort_keys=True))

insert_into_directors = f"""
    INSERT INTO directors (name)
    VALUES (%s);
    """

# conn = psycopg2.connect(host=HOSTNAME, port=PORT, database=DBNAME, user=USERNAME, password=PASSWORD)
# cursor = conn.cursor()

# director
# director_name = data_dict[0]["credits"]["Director:"][0]["name"]
# cursor.execute(insert_into_directors, director_name)

# writers
# writers = data_dict[0]["credits"]["Writers:"]
# for writer in writers:
#     if re.search(r"/name/", writer["link"]):
#         writer_name = writer["name"]

# stars
# stars = data_dict[0]["credits"]["Stars:"]
# for star in stars:
#     if re.search(r"/name/", star["link"]):
#         star_name = star["name"]

# genres
# genres = data_dict[0]["genres"]  # ['Animation', 'Adventure', 'Fantasy']

# rating value
# data_dict[0]["ratingValue"]

# rating count
# data_dict[0]["ratingCount"]

# name
# data_dict[0]["name"]

# is series
# data_dict[0]["isSeries"]

# duration 
# data_dict[0]["duration"]

# summary_text 
# data_dict[0]["summary_text"]

# movie_rated
# data_dict[0]["movie_rated"]  # need to fix

