import datetime
from typing import Iterator

from utils.connection_etl import postgres_connection


class Extractor:
    """Класс для извлечения данных из PostgresSQL"""

    def __init__(self, psql_dsn, chunk_size: int, storage_state,
                 verbose) -> None:
        self.chunk_size = chunk_size
        self.state = storage_state
        self.dsn = psql_dsn
        self.verbose = verbose

    def extract(self,
                extract_timestamp: datetime.datetime) -> Iterator:
        """
        Метод чтения данных пачками.
        Ищем строки, удовлетворяющие условию - при нахождении записываем
        в хранилище состояния id
        """

        with postgres_connection(self.dsn) as pg_conn, \
            pg_conn.cursor() as cursor:
            sql = f"""
                    SELECT 
                        fw.id,
                        fw.rating as imdb_rating, 
                        json_agg(DISTINCT g.name) as genre,
                        fw.title,
                        fw.description,
                        fw.modified,
                        string_agg(DISTINCT CASE WHEN pfw.role = 'director' THEN p.full_name ELSE '' END, ',') AS director,
                        array_remove(COALESCE(array_agg(DISTINCT CASE WHEN pfw.role = 'actor' THEN p.full_name END) FILTER (WHERE p.full_name IS NOT NULL)), NULL) AS actors_names,
                        array_remove(COALESCE(array_agg(DISTINCT CASE WHEN pfw.role = 'writer' THEN p.full_name END) FILTER (WHERE p.full_name IS NOT NULL)), NULL) AS writers_names,
                        concat('[', string_agg(DISTINCT CASE WHEN pfw.role = 'actor' THEN json_build_object('id', p.id, 'name', p.full_name) #>> '{{}}' END, ','), ']') AS actors,
                        concat('[', string_agg(DISTINCT CASE WHEN pfw.role = 'writer' THEN json_build_object('id', p.id, 'name', p.full_name) #>> '{{}}' END, ','), ']') AS writers,
                        GREATEST(MAX(fw.modified), MAX(g.modified), MAX(p.modified)) AS last_modified
                    FROM 
                        content.film_work as fw
                        LEFT JOIN content.genre_film_work gfm ON fw.id = gfm.film_work_id
                        LEFT JOIN content.genre g ON gfm.genre_id = g.id
                        LEFT JOIN content.person_film_work pfw ON fw.id = pfw.film_work_id
                        LEFT JOIN content.person p ON pfw.person_id = p.id
                    GROUP BY fw.id
                    HAVING GREATEST(MAX(fw.modified), MAX(g.modified), MAX(p.modified)) > '{str(extract_timestamp)}' 
                    ORDER BY GREATEST(MAX(fw.modified), MAX(g.modified), MAX(p.modified)) DESC;
                    """
            cursor.execute(sql)

            while True:
                rows = cursor.fetchmany(self.chunk_size)
                if not rows:
                    self.verbose.info('изменений не найдено')
                    break
                self.verbose.info(f'извлечено {len(rows)} строк')
                yield rows
