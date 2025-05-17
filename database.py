import sqlite3
from dataclasses import dataclass
from typing import Optional

DATABASE_NAME = 'merged.db'


@dataclass
class Place:
    id: int
    category: str
    name: str
    address: str
    rating: float
    reviews_count: int
    latitude: float
    longitude: float
    image: Optional[str]
    description: Optional[str]
    distance_km: float


def get_nearest_eat_location(user_lat, user_lon):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        q = '''SELECT id,
                      category,
                      name,
                      address,
                      rating,
                      reviews,
                      lon      AS longitude,
                      lat      AS latitude,
                      picture,
                      6371 * ACOS(
                              SIN(RADIANS(?)) * SIN(RADIANS(lat)) +
                              COS(RADIANS(?)) * COS(RADIANS(lat)) *
                              COS(RADIANS(lon) - RADIANS(?))
                             ) AS distance_km,
                      description
               FROM places
               WHERE distance_km < 2
               ORDER BY distance_km ASC LIMIT 1;
            '''
        cursor.execute(q, (user_lat, user_lat, user_lon))

        row = cursor.fetchone()
        if row:
            return Place(
                id=row[0],
                category=row[1],
                name=row[2],
                address=row[3],
                rating=row[4],
                reviews_count=row[5],
                longitude=row[6],
                latitude=row[7],
                image=row[8],
                distance_km=row[9],
                description=row[10],
            )
        return None

    except sqlite3.Error as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None
    finally:
        conn.close()


def get_another_nearest_eat_location(user_lat, user_lon, exclude_ids):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        exclude_ids = exclude_ids if exclude_ids else (-1,)

        q = '''SELECT id,
                      category,
                      name,
                      address,
                      rating,
                      reviews,
                      lon AS longitude,
                      lat AS latitude,
                      picture,
                      6371 * ACOS(
                          SIN(RADIANS(?)) * SIN(RADIANS(lat)) +
                          COS(RADIANS(?)) * COS(RADIANS(lat)) *
                          COS(RADIANS(lon) - RADIANS(?))
                      ) AS distance_km,
                      description 
               FROM places
               WHERE id NOT IN ({})
               AND distance_km < 2
               ORDER BY distance_km ASC LIMIT 1;
            '''.format(','.join(['?'] * len(exclude_ids)))

        params = (user_lat, user_lat, user_lon) + tuple(exclude_ids)

        cursor.execute(q, params)
        row = cursor.fetchone()

        if row:
            return Place(
                id=row[0],
                category=row[1],
                name=row[2],
                address=row[3],
                rating=row[4],
                reviews_count=row[5],
                longitude=row[6],
                latitude=row[7],
                image=row[8],
                distance_km=row[9],
                description=row[10],
            )
        return None

    except sqlite3.Error as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None
    finally:
        conn.close()


def get_top_rated_eat_location(user_lat: float, user_lon: float, excluded_ids: list = None):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        excluded_ids = excluded_ids or []

        # Базовый запрос без фильтрации по исключенным ID
        base_query = '''SELECT id,
                               category,
                               name,
                               address,
                               rating,
                               reviews,
                               lon      AS longitude,
                               lat      AS latitude,
                               picture,
                               6371 * ACOS(
                                       SIN(RADIANS(?)) * SIN(RADIANS(lat)) +
                                       COS(RADIANS(?)) * COS(RADIANS(lat)) *
                                       COS(RADIANS(lon) - RADIANS(?))
                                      ) AS distance_km,
                               description
                        FROM places
                        WHERE distance_km < 2 {}
                        ORDER BY rating DESC LIMIT 1; \
                     '''

        # Добавляем условие для исключения ID, если они есть
        if excluded_ids:
            id_placeholders = ','.join(['?'] * len(excluded_ids))
            where_clause = f'AND id NOT IN ({id_placeholders})'
            query = base_query.format(where_clause)
            params = (user_lat, user_lat, user_lon) + tuple(excluded_ids)
        else:
            query = base_query.format('')
            params = (user_lat, user_lat, user_lon)

        cursor.execute(query, params)
        row = cursor.fetchone()

        if row:
            return Place(
                id=row[0],
                category=row[1],
                name=row[2],
                address=row[3],
                rating=row[4],
                reviews_count=row[5],
                longitude=row[6],
                latitude=row[7],
                image=row[8],
                distance_km=row[9],
                description=row[10],
            )
        return None

    except sqlite3.Error as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None
    finally:
        conn.close()
