from minio import Minio
import json
import io


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

def get_obj_filepaths(objects):
    '''
    Parameters
    ----------
    objects: MinIO Object
        An iterator of Objects stored in MinIO Bucket
    '''
    filepaths = []
    for obj in objects:
    # {'_bucket_name': 'data', '_object_name': 'imdb/2021-04-03/anime_1.json', 
    #   '_last_modified': datetime.datetime(2021, 3, 18, 1, 42, 59, 439000, tzinfo=datetime.timezone.utc), 
    #   '_etag': '85951813368733551d7c8ada22923374', '_size': 118618497, '_metadata': {}, '_version_id': None, 
    #   '_is_latest': None, '_storage_class': 'STANDARD', '_owner_id': '', '_owner_name': '', '_content_type': None}
        if obj.object_name.split('.')[-1] == "json":
            filepaths.append(f"{obj.bucket_name}/{obj.object_name}")  
    return filepaths 

# filepaths = get_obj_filepaths(objects)
# print(filepaths)
for obj in objects:
    o = client.get_object(BUCKET_NAME, obj.object_name)
    data = json.load(io.BytesIO(o.data))
    data_dict = json.loads(data)
    for d in data_dict:
        print(d.keys())
        print("\n")
    # print(json.dumps(data, indent=4, sort_keys=True))
