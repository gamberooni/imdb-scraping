import os
import pandas as pd
import time

project_dir = os.path.dirname(__file__)  # the directory that includes all the AI services project

invalid_chars = {
    '%': 'PCT_', 
    '(': '_', 
    ')': '_'
    }

valid_extensions = ['.csv', '.xlsx']

def drop_schema_if_exists(schema_name, conn, cursor):
    DROP_SCHEMA = f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;"
    cursor.execute(DROP_SCHEMA)
    conn.commit()
    print(f"Dropped schema: {schema_name}")

def create_schema(schema_name, conn, cursor):
    CREATE_SCHEMA = f"CREATE SCHEMA IF NOT EXISTS {schema_name};"
    cursor.execute(CREATE_SCHEMA)
    conn.commit()
    print(f"Created schema: {schema_name}")

def get_dir_name(file):
    current_path = os.path.dirname(os.path.realpath(file))
    sep = os.path.sep
    dir_name = current_path.split(sep)[-1]
    return dir_name

def check_invalid_header(df):
    columns = list(df.columns.values)
    for key in invalid_chars:
        for c in columns:
            if key in c:
                return True
    return False

def replace_header(df):
    columns = list(df.columns.values)
    for i in invalid_chars.items():
        columns = [c.replace(i[0], i[1]) for c in columns]
    df.columns = columns
    return df

def upload_files(current_dir, DB_URI):
    full_path = project_dir + os.path.sep + current_dir  # e.g. /path/to/projects/mead_johnson
    start_time = time.time()
    for file in os.listdir(full_path):
        if file.endswith(tuple(valid_extensions)):
            print(f"Processing file: {file}")
            try:
                df = pd.read_csv(full_path + '/' + file)
            except: 
                df = pd.read_excel(full_path + '/' + file, engine='openpyxl')
            if check_invalid_header(df):
                replace_header(df)
            tablename = file.split('.')[0].lower()  # get the filename without the '.csv' extension and to lower case
            tablename = '_'.join(tablename.split(' '))  # replace spaces with '_'
            df.to_sql(file.split('.')[0].lower(), DB_URI, schema=current_dir, if_exists='replace', index=False, method='multi')
    print("--- Job took %s seconds ---" % (time.time() - start_time))
