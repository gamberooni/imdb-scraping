import os
from conf import SCHEMA_NAME


drop_schema_sql = f"DROP SCHEMA IF EXISTS {SCHEMA_NAME} CASCADE;"
create_schema_sql = f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME};"
set_search_path_sql = f"SET search_path TO {SCHEMA_NAME};"

# CREATE TABLES
create_directors_table = f"""
    CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.directors (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) UNIQUE,
        born_year SMALLINT,
        born_month VARCHAR(20),
        born_day SMALLINT);
    """         

create_stars_table = f"""
    CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.stars (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) UNIQUE NOT NULL,
        born_year SMALLINT,
        born_month VARCHAR(20),
        born_day SMALLINT);
    """                           

create_writers_table = f"""
    CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.writers (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) UNIQUE NOT NULL,
        born_year SMALLINT,
        born_month VARCHAR(20),
        born_day SMALLINT);
    """

create_genres_table = f"""
    CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.genres (
        id SERIAL PRIMARY KEY,
        genre VARCHAR(50) UNIQUE NOT NULL);
    """

create_titles_table = f"""
    CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.titles (
        id SERIAL PRIMARY KEY,
        scrape_ts TIMESTAMP,
        duration SMALLINT,
        is_series BOOLEAN,
        name VARCHAR(500) NOT NULL,
        url VARCHAR(100) NOT NULL,
        poster_url VARCHAR(800),
        rating_count INT,
        rating_value FLOAT(2),
        release_date VARCHAR(50),
        release_year SMALLINT,
        summary_text VARCHAR);
    """

create_titles_directors_tables = f"""
    CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.titles_directors (
        title_id INT REFERENCES {SCHEMA_NAME}.titles (id),
        director_id INT REFERENCES {SCHEMA_NAME}.directors (id));
    """    

create_titles_stars_tables = f"""
    CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.titles_stars (
        title_id INT REFERENCES {SCHEMA_NAME}.titles (id),
        star_id INT REFERENCES {SCHEMA_NAME}.stars (id));
    """               

create_titles_writers_tables = f"""
    CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.titles_writers (
        title_id INT REFERENCES {SCHEMA_NAME}.titles (id),
        writer_id INT REFERENCES {SCHEMA_NAME}.writers (id));
    """

create_titles_genres_tables = f"""
    CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.titles_genres (
        title_id INT REFERENCES {SCHEMA_NAME}.titles (id),
        genre_id SMALLINT REFERENCES {SCHEMA_NAME}.genres (id));
    """   

# INSERT INTO TABLEs
insert_into_directors = f"""
    INSERT INTO {SCHEMA_NAME}.directors (name, born_year, born_month, born_day)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (name)
    DO NOTHING;
    """

insert_into_writers = f"""
    INSERT INTO {SCHEMA_NAME}.writers (name, born_year, born_month, born_day)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (name)
    DO NOTHING;
    """    

insert_into_stars = f"""
    INSERT INTO {SCHEMA_NAME}.stars (name, born_year, born_month, born_day)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (name)
    DO NOTHING;
    """    

insert_into_genres = f"""
    INSERT INTO {SCHEMA_NAME}.genres (genre)
    VALUES (%s)
    ON CONFLICT (genre)
    DO NOTHING;
    """    

insert_into_titles = f"""
    INSERT INTO {SCHEMA_NAME}.titles (scrape_ts, duration, is_series, name, url, poster_url, rating_count, rating_value, release_date, release_year, summary_text)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """ 

insert_into_titles_directors = f"""
    INSERT INTO {SCHEMA_NAME}.titles_directors (title_id, director_id)
    SELECT t.id, d.id 
    FROM {SCHEMA_NAME}.titles t, {SCHEMA_NAME}.directors d
    WHERE t.name = %s
        AND d.name = %s
    """ 

insert_into_titles_stars = f"""
    INSERT INTO {SCHEMA_NAME}.titles_stars (title_id, star_id)
    SELECT t.id, s.id 
    FROM {SCHEMA_NAME}.titles t, {SCHEMA_NAME}.stars s
    WHERE t.name = %s
        AND s.name = %s
    """ 

insert_into_titles_writers = f"""
    INSERT INTO {SCHEMA_NAME}.titles_writers (title_id, writer_id)
    SELECT t.id, w.id 
    FROM {SCHEMA_NAME}.titles t, {SCHEMA_NAME}.writers w
    WHERE t.name = %s
        AND w.name = %s
    """ 

insert_into_titles_genres = f"""
    INSERT INTO {SCHEMA_NAME}.titles_genres (title_id, genre_id)
    SELECT t.id, g.id 
    FROM {SCHEMA_NAME}.titles t, {SCHEMA_NAME}.genres g
    WHERE t.name = %s
        AND g.genre = %s
    """ 

create_tables_sql = [
    create_directors_table, 
    create_stars_table, 
    create_writers_table, 
    create_genres_table, 
    create_titles_table,
    create_titles_directors_tables,
    create_titles_stars_tables,
    create_titles_writers_tables,
    create_titles_genres_tables,
    ]                                