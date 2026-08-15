from Baanknetbot.baanknet_script import get_properties_total_page_count, get_auction_id_list, \
    property_insertion_orchestrator
from Baanknetbot.database_config import get_postgresql_database_connection
from Baanknetbot.utils import get_payload
import asyncio


async def bot_orchestrator():
    try:
        print("------------------system started to fetch property details------------------")
        database_connection = await get_postgresql_database_connection()
        print("------------------Obtained database connection -----------------------------")
        print("--------------------Fetching auction_id of all the properties----------------")
        total_page_count = get_properties_total_page_count(payload=get_payload())
        print("------------------Fetching auction_id of all the properties---------------------")
        auction_id_list =  await get_auction_id_list(database_connection=database_connection,total_page_count=total_page_count, payload=get_payload())
        print("--------------------Auction id list Fetched ----------------------")
        await property_insertion_orchestrator(auction_id_list=auction_id_list,pg_connection=database_connection)
    except Exception as e:
        raise e
#orchestration file for running baanknet script
if __name__ == "__main__":
    asyncio.run(bot_orchestrator())











