import random
from datetime import datetime

import requests


def get_districts_based_on_state_id(state_id:int)->list[dict]:
    try:
        district_list = []
        districts_endpoint_url = "https://baanknet.com/api/v1/common/cities/search"
        response = requests.post(url=districts_endpoint_url,json={"stateId":state_id ,"cityName": ""})
        response.raise_for_status()
        response_data = response.json()
        data_list = response_data.get("data").get("data")

        unique_district_id = []
        for district in data_list:
            district_id = district.get('_source').get("districtId")
            if district_id not in unique_district_id:
                unique_district_id.append(district_id)
                district_list.append({"district_id":(district.get('_source').get("districtId")),"state_id":state_id,"district":district.get('_source').get("district")})
        return district_list
    except requests.exceptions.RequestException as e:
        print("Request Failed due to error",e)
        raise e
    except Exception as e:
        print("Request Failed due to error",e)
        raise e


def get_payload():
    return {"search": {"stateId": 31, "propTypeOfActionId": []}, "range": {}, "sort": {"type": "mostrecent","postedSince": "2026-08-08"},"page": 1, "limit": 10}

def get_random_seconds():
    return random.randint(1,120)

def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )