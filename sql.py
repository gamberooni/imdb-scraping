schemaName = "imdb"

drop_schema = f"DROP SCHEMA IF EXISTS {schemaName} CASCADE;"
create_schema = f"CREATE SCHEMA IF NOT EXISTS {schemaName};"
set_search_path = f"SET search_path TO {schemaName};"

create_directors_table = f"""
    CREATE TABLE IF NOT EXISTS directors (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL);
    """         

create_stars_table = f"""
    CREATE TABLE IF NOT EXISTS stars (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL);
    """                           

create_writers_table = f"""
    CREATE TABLE IF NOT EXISTS writers (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL);
    """

create_genres_table = f"""
    CREATE TABLE IF NOT EXISTS genres (
        id SERIAL PRIMARY KEY,
        genre VARCHAR(50) NOT NULL);
    """

create_titles_table = f"""
    CREATE TABLE IF NOT EXISTS titles (
        id SERIAL PRIMARY KEY,
        director_id INT REFERENCES directors (id),
        star_id INT REFERENCES stars (id),
        writer_id INT REFERENCES writers (id),
        genre_id SMALLINT REFERENCES genres (id),
        duration SMALLINT,
        is_series BOOLEAN,
        movie_rated VARCHAR(10),
        name VARCHAR(50) NOT NULL,
        rating_count INT,
        rating_value FLOAT(2),
        release_date VARCHAR(15),
        summary_text VARCHAR);
    """

create_titles_directors_tables = f"""
    CREATE TABLE IF NOT EXISTS titles_directors (
        title_id INT,
        director_id INT);
    """    

create_titles_stars_tables = f"""
    CREATE TABLE IF NOT EXISTS titles_stars (
        title_id INT,
        star_id INT);
    """               

create_titles_writers_tables = f"""
    CREATE TABLE IF NOT EXISTS titles_writers (
        title_id INT,
        writer_id INT);
    """

create_titles_genres_tables = f"""
    CREATE TABLE IF NOT EXISTS titles_writers (
        title_id INT,
        genre_id INT);
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