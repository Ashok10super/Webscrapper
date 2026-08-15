import os
import time
from datetime import datetime, timezone

import asyncpg
import requests
from requests.adapters import HTTPAdapter
from dotenv import load_dotenv
from Baanknetbot.utils import get_random_seconds, parse_datetime
from Baanknetbot.service import fetch_row_using_query, insert_row_using_query

load_dotenv()

session = requests.session()
session.mount('https://', HTTPAdapter(max_retries=3))
headers = {"Content-Type": "application/json",
           "referer": "https://baanknet.com/"}
session.headers.update(headers)


def get_properties_total_page_count(payload=None)->int:
    try:
        url = os.getenv("PROPERTIES_FILTER_ENDPOINT")
        # Step 1: Fetch data from API
        response = session.post(url=url, json=payload, headers=headers, verify=False)

        if response.status_code == 200:
            print("Request successful")
            data = response.json()  # Convert JSON response to Python dictionary
            total_pages = data.get("data").get("totalPages")
            print(total_pages)
            return total_pages
        else:
            raise Exception("Api is down or changed their config")
    except requests.exceptions.RequestException as e:
        raise e
    except Exception as e:
        raise e

async def get_auction_id_list(database_connection:asyncpg.connection.Connection,total_page_count,payload=None)->list:
    try:
        url = os.getenv("PROPERTIES_FILTER_ENDPOINT")
        auction_id_list = []
        for page in range(1, total_page_count + 1):
            payload.update({"page": page})
            response = session.post(url=url, json=payload, headers=headers, verify=False)
            if response.status_code == 200:
                data = response.json()
                property_data = data.get("data").get("data")
                for property in property_data:
                    auction_id = property.get("_source").get('auctionId')
                    #check if the auction_id already exists in the db or not
                    if await is_auction_id_available(auction_id,database_connection):
                        print("auction_id already exists",auction_id)
                    else:
                        if auction_id:
                            auction_id_list.append(auction_id)
            else:
                raise Exception("Api is down or changed their config")

            #To mimic human like interaction with the server wait for random seconds in between each requests
            # random_seconds = get_random_seconds()
            # print(random_seconds)
            # time.sleep(random_seconds)
        return auction_id_list
    except requests.exceptions.RequestException as e:
        raise e
    except Exception as e:
        raise e


async def property_insertion_orchestrator(auction_id_list,pg_connection):
    try:
        print(auction_id_list)
        property_endpoint = os.getenv("PROPERTY_ENDPOINT")
        iterator =1
        for auction_id in auction_id_list:
            print("Processing property=>",iterator)
            response = session.get(url=property_endpoint+f"/{auction_id}",headers=headers, verify=False)
            if response.status_code == 200:
                data = response.json()
                property_data = data.get("data")
                city_id = property_data.get("cityId")
                city_name = property_data.get("cityName")
                district_id = property_data.get("districtId")
                #step 1: insert the city details of the property with the city id to the city table
                is_city_exist = await check_and_insert_city(city_id,district_id,city_name,pg_connection)
                if is_city_exist:
                    #step 2 if city exist then insert auction details
                    auction_details = (
                        property_data.get("auctionId"),
                        parse_datetime(property_data.get("auctionFrom")),
                        parse_datetime(property_data.get("auctionTo")),
                        parse_datetime(property_data.get("auctionVerifiedOn")),
                        property_data.get("auctionBranch"),
                        property_data.get("checkerName"),
                        property_data.get("checkerDesignation"),
                        float(property_data["emd"]) if property_data.get("emd") else None,
                        parse_datetime(property_data.get("emdStart")),
                        parse_datetime(property_data.get("emdEnd")),
                        property_data.get("reservePrice"),
                        property_data.get("incrementPrice"),
                        property_data.get("inspectionName"),
                        property_data.get("inspectionMobileNo"),
                        property_data.get("inspectionBranch"),
                        property_data.get("auctionType"),
                        datetime.now(timezone.utc),
                        None
                    )
                    await insert_auction_details(auction_details,pg_connection)


                    #step 3 if the auction details inserted successfully now insert the properties

                    property_details = (
                        property_data.get("propertyDetailId"),
                        property_data.get("auctionId"),
                        property_data.get("propertyBankId"),
                        property_data.get("propertyUniqueId"),
                        property_data.get("pincode"),
                        property_data.get("stateId"),
                        property_data.get("districtId"),
                        property_data.get("cityId"),
                        property_data.get("locality"),
                        property_data.get("address"),
                        property_data.get("propertyPossessionType"),
                        property_data.get("propertyType"),
                        property_data.get("propertySubType"),
                        float(property_data["carpetAreaSqft"]) if property_data.get("carpetAreaSqft") else None,
                        float(property_data["builtupAreaSqft"]) if property_data.get("builtupAreaSqft") else None,
                        False,  # is_approved
                        None,  # approved_by
                        None,  # listed_date
                        None,  # created_by
                        None,  # modified_by
                        datetime.now(timezone.utc),  # created_at
                        None,  # modified_at
                    )
                    await insert_property(property_details,pg_connection)
                    print("Property inserted")
                    bank_details = (
                        property_data.get("propertyBankId"),
                        property_data.get("propertyDetailId"),
                        property_data.get("propertyBankName"),
                        property_data.get("propertyBranchName"),
                        property_data.get("borrowerName"),
                        property_data.get("borrowerAddress"),
                        property_data.get("isLoanAvailable"),
                        str(property_data.get("percentageOfLoan")),
                    )
                    await insert_bank_details(bank_details, pg_connection)

                    #save property documents
                    for doc in property_data.get("auctionDocuments"):
                        document_url  = doc.get("url")
                        if document_url:
                            await insert_url(table_name="auction_document_link",property_id=property_data.get("propertyDetailId"),url=document_url,pg_connection=pg_connection)
                    for media in property_data.get("propertyMedia"):
                        media_url = media.get("url")
                        if media_url:
                            await insert_url(table_name="auction_document_link",property_id=property_data.get("propertyDetailId"),url=media_url,pg_connection=pg_connection)
                    iterator+=1
        print("Total property inserted: ", iterator)
    except Exception as e:
        print(e)


async def check_and_insert_city(
    city_id: int,
    district_id:int,
    city_name: str,
    pg_connection: asyncpg.Connection
):
    try:
        if not city_id:
            return False

        query = """
            SELECT city_id
            FROM city
            WHERE city_id = $1
        """

        city = await fetch_row_using_query(
            query,
            pg_connection,
            city_id
        )

        if city:
            return True

        insert_query = """
            INSERT INTO city (
                city_id,
                district_id,
                city
            )
            VALUES ($1, $2, $3)
        """

        await insert_row_using_query(
            insert_query,
            pg_connection,
            city_id,
            district_id,
            city_name
        )

        return True

    except asyncpg.PostgresError:
        raise


async def insert_auction_details(
    auction_details: tuple,
    pg_connection: asyncpg.Connection
):
    query = """
        INSERT INTO auction_details (
            auction_id,
            auction_start_date,
            auction_end_date,
            auction_verified_on,
            auction_branch,
            checker_name,
            checker_designation,
            emd_amount,
            emd_start_date,
            emd_end_date,
            reserve_price,
            increment_price,
            inspector_name,
            inspector_mobile_no,
            inspector_branch,
            auction_type,
            created_at,
            updated_at
        )
        VALUES (
            $1, $2, $3, $4,
        $5, $6, $7, $8,
            $9, $10, $11, $12,
            $13, $14, $15, $16,
            $17 , $18
        )
    """
    try:
        await pg_connection.execute(
            query,
            *auction_details
            )
    except asyncpg.PostgresError as e:
        raise e



async def insert_bank_details(
    bank_details: tuple,
    pg_connection: asyncpg.Connection
):
    query = """
        INSERT INTO bank_details (
            bank_id,
            property_id,
            bank_name,
            branch_name,
            borrower_name,
            borrower_address,
            is_loan_available,
            percentage_of_loan
        )
        VALUES (
            $1, $2, $3, $4, $5, $6, $7,$8
        )
    """
    try:
        await pg_connection.execute(
                query,
                *bank_details
            )
    except asyncpg.PostgresError as e:
        raise e


async def insert_property(
    property_details: tuple,
    pg_connection: asyncpg.Connection
):
    query = """
        INSERT INTO properties (
            property_id,
            auction_id,
            bank_id,
            property_unique_id,
            property_pincode,
            state_id,
            district_id,
            city_id,
            locality,
            property_address,
            property_possession_type,
            property_type,
            property_sub_type,
            property_carpet_area_sqft,
            property_build_up_area_sqft,
            is_approved,
            approved_by,
            listed_date,
            created_by,
            modified_by,
            created_at,
            updated_at
        )
        VALUES (
            $1, $2, $3, $4,
            $5, $6, $7, $8,
            $9, $10, $11, $12,
            $13, $14, $15, $16,
            $17, $18, $19, $20,
            $21, $22
        )
        """
    try:
        await pg_connection.execute(
            query,
            *property_details
        )
    except asyncpg.PostgresError as e :
        raise e

async def is_auction_id_available(
    auction_id: int,
    pg_connection: asyncpg.Connection
)->bool:
    try:
        query = """SELECT 1 FROM auction_details WHERE auction_id = $1 LIMIT 1"""
        row = await fetch_row_using_query(
            query,pg_connection,auction_id )
        if row:
            return True
        else:
            return False
    except Exception as e:
        raise e

import asyncpg


async def insert_url(
    table_name: str,
    property_id: int,
    url: str,
    pg_connection: asyncpg.Connection
):
    try:
        query = f"""
            INSERT INTO {table_name} (
                property_id,
                document_url
            )
            VALUES ($1, $2)
        """

        await pg_connection.execute(
            query,
            property_id,
            url
        )

    except asyncpg.PostgresError as e:
        raise e