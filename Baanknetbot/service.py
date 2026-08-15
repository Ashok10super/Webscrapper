import asyncpg

async def insert_district(district_list:list[dict],postgres_sql_connection:asyncpg.connection.Connection):
    try:
        query = """
                INSERT INTO district (district_id,state_id, district)
                VALUES ($1, $2, $3)
            """
        values = [
            (
                item["district_id"],
                item["state_id"],
                item["district"]
            )
            for item in district_list
        ]
        await postgres_sql_connection.executemany(query, values)

        print("Successfully inserted district")

    except asyncpg.PostgresError as err:
        print(err)


async def fetch_row_using_query(
    query: str,
    postgres_sql_connection: asyncpg.Connection,
    *args
) -> asyncpg.Record | None:
    try:
        return await postgres_sql_connection.fetchrow(query, *args)
    except asyncpg.PostgresError as e:
        raise e


async def insert_row_using_query(
    query: str,
    postgres_sql_connection: asyncpg.Connection,
    *args
) -> str:
    try:
        result = await postgres_sql_connection.execute(query, *args)
        return result

    except asyncpg.PostgresError:
        raise