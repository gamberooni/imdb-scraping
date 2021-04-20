import os
from conf import SCHEMA_NAME

schemaName = SCHEMA_NAME

drop_schema = f"DROP SCHEMA IF EXISTS {schemaName} CASCADE;"
create_schema = f"CREATE SCHEMA IF NOT EXISTS {schemaName};"
set_search_path = f"SET search_path TO {schemaName};"


# CREATE TABLES
create_directors_table = f"""
    CREATE TABLE IF NOT EXISTS directors (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) UNIQUE,
        born_year SMALLINT,
        born_month VARCHAR(20),
        born_day SMALLINT);
    """         

create_stars_table = f"""
    CREATE TABLE IF NOT EXISTS stars (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) UNIQUE NOT NULL,
        born_year SMALLINT,
        born_month VARCHAR(20),
        born_day SMALLINT);
    """                           

create_writers_table = f"""
    CREATE TABLE IF NOT EXISTS writers (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) UNIQUE NOT NULL,
        born_year SMALLINT,
        born_month VARCHAR(20),
        born_day SMALLINT);
    """

create_genres_table = f"""
    CREATE TABLE IF NOT EXISTS genres (
        id SERIAL PRIMARY KEY,
        genre VARCHAR(50) UNIQUE NOT NULL);
    """

create_titles_table = f"""
    CREATE TABLE IF NOT EXISTS titles (
        id SERIAL PRIMARY KEY,
        scrape_ts TIMESTAMP,
        duration SMALLINT,
        is_series BOOLEAN,
        name VARCHAR(500) NOT NULL,
        url VARCHAR(100) NOT NULL,
        rating_count INT,
        rating_value FLOAT(2),
        release_date VARCHAR(50),
        release_year SMALLINT,
        summary_text VARCHAR);
    """

create_titles_directors_tables = f"""
    CREATE TABLE IF NOT EXISTS titles_directors (
        title_id INT REFERENCES titles (id),
        director_id INT REFERENCES directors (id));
    """    

create_titles_stars_tables = f"""
    CREATE TABLE IF NOT EXISTS titles_stars (
        title_id INT REFERENCES titles (id),
        star_id INT REFERENCES stars (id));
    """               

create_titles_writers_tables = f"""
    CREATE TABLE IF NOT EXISTS titles_writers (
        title_id INT REFERENCES titles (id),
        writer_id INT REFERENCES writers (id));
    """

create_titles_genres_tables = f"""
    CREATE TABLE IF NOT EXISTS titles_genres (
        title_id INT REFERENCES titles (id),
        genre_id SMALLINT REFERENCES genres (id));
    """   

# INSERT INTO TABLEs
insert_into_directors = f"""
    INSERT INTO directors (name, born_year, born_month, born_day)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (name)
    DO NOTHING;
    """

insert_into_writers = f"""
    INSERT INTO writers (name, born_year, born_month, born_day)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (name)
    DO NOTHING;
    """    

insert_into_stars = f"""
    INSERT INTO stars (name, born_year, born_month, born_day)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (name)
    DO NOTHING;
    """    

insert_into_genres = f"""
    INSERT INTO genres (genre)
    VALUES (%s)
    ON CONFLICT (genre)
    DO NOTHING;
    """    

insert_into_titles = f"""
    INSERT INTO titles (scrape_ts, duration, is_series, name, url, rating_count, rating_value, release_date, release_year, summary_text)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """ 

insert_into_titles_directors = f"""
    INSERT INTO titles_directors (title_id, director_id)
    SELECT t.id, d.id 
    FROM titles t, directors d
    WHERE t.name = %s
        AND d.name = %s
    """ 

insert_into_titles_stars = f"""
    INSERT INTO titles_stars (title_id, star_id)
    SELECT t.id, s.id 
    FROM titles t, stars s
    WHERE t.name = %s
        AND s.name = %s
    """ 

insert_into_titles_writers = f"""
    INSERT INTO titles_writers (title_id, writer_id)
    SELECT t.id, w.id 
    FROM titles t, writers w
    WHERE t.name = %s
        AND w.name = %s
    """ 

insert_into_titles_genres = f"""
    INSERT INTO titles_genres (title_id, genre_id)
    SELECT t.id, g.id 
    FROM titles t, genres g
    WHERE t.name = %s
        AND g.genre = %s
    """ 

create_tables = [
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