import os

schemaName = os.getenv('SCHEMA_NAME', "imdb")

drop_schema = f"DROP SCHEMA IF EXISTS {schemaName} CASCADE;"
create_schema = f"CREATE SCHEMA IF NOT EXISTS {schemaName};"
set_search_path = f"SET search_path TO {schemaName};"


# CREATE TABLES
create_directors_table = f"""
    CREATE TABLE IF NOT EXISTS directors (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) UNIQUE);
    """         

create_stars_table = f"""
    CREATE TABLE IF NOT EXISTS stars (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) UNIQUE NOT NULL);
    """                           

create_writers_table = f"""
    CREATE TABLE IF NOT EXISTS writers (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) UNIQUE NOT NULL);
    """

create_genres_table = f"""
    CREATE TABLE IF NOT EXISTS genres (
        id SERIAL PRIMARY KEY,
        genre VARCHAR(50) UNIQUE NOT NULL);
    """

create_titles_table = f"""
    CREATE TABLE IF NOT EXISTS titles (
        id SERIAL PRIMARY KEY,
        duration VARCHAR(10),
        is_series BOOLEAN,
        name VARCHAR(500) NOT NULL,
        rating_count INT,
        rating_value FLOAT(2),
        release_date VARCHAR(50),
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
        star_id INT);
    """               

create_titles_writers_tables = f"""
    CREATE TABLE IF NOT EXISTS titles_writers (
        title_id INT REFERENCES titles (id),
        writer_id INT REFERENCES writers (id));
    """

create_titles_genres_tables = f"""
    CREATE TABLE IF NOT EXISTS titles_writers (
        title_id INT REFERENCES titles (id),
        genre_id SMALLINT REFERENCES genres (id));
    """   

# INSERT INTO TABLEs
insert_into_directors = f"""
    INSERT INTO directors (name)
    VALUES (%s)
    ON CONFLICT (name)
    DO NOTHING;
    """

insert_into_writers = f"""
    INSERT INTO writers (name)
    VALUES (%s)
    ON CONFLICT (name)
    DO NOTHING;
    """    

insert_into_stars = f"""
    INSERT INTO stars (name)
    VALUES (%s)
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
    INSERT INTO titles (duration, is_series, name, rating_count, rating_value, release_date, summary_text)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
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