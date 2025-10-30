import requests
from dotenv import load_dotenv
load_dotenv()
import os
import time

def check_area_with_crm(area):#get all the areas from the list of available areas
    print(area)
    zoho_url =  "https://www.zohoapis.in/crm/v7/Area/search?criteria=Name:equals:"+str(area)

    header = {
        'Authorization':os.getenv('ZOHO_ACCESS_TOKEN')
    }
    try:
        response = requests.get(url=zoho_url,headers=header,verify=True)
        response.raise_for_status()
        status_code = response.status_code

        if status_code == 200:
          data = response.json()
          print("Response from area",data)
          return data
        else:
            return False  
    except Exception as e:
        print("Expection from area->",e)    

def check_hobli(area):
    zoho_url =  "https://www.zohoapis.in/crm/v7/Hobli/search?criteria=Name:equals:"+str(area)

    header = {
        'Authorization':os.getenv('ZOHO_ACCESS_TOKEN')
    }
    try:
        response = requests.get(url=zoho_url,headers=header,verify=True)
        staus_code = response.status_code

        if staus_code == 200:
           data = response.json()
           print("Response from hobl",data)
           return data
        else:
            return False    
    except Exception as e:
        print("Expectation from hobli",e)    

def get_direction(hobli):
    zoho_url = "https://www.zohoapis.in/crm/v7/Hobli/search?criteria=id:equals:"+hobli

    header = {
        'Authorization':os.getenv('ZOHO_ACCESS_TOKEN')
    }
    try:
        response = requests.get(url=zoho_url,headers=header,verify=True)
        staus_code = response.status_code
        data = response.json()
        og_data = data.get('data')[0]
        direction_obj = og_data.get('Direction') 
        direction_id = direction_obj.get('id')
        print("Direction_id->",direction_id)
        return direction_id
    except Exception as e:
        print(e)    





def update_accounts(area,acc_id):
    print("Account_id->",acc_id)
    area_dict = area.get('data')[0]
    area_og = area_dict.get('id')
    hobli_obj = area_dict.get('Hobli')
    hobli_id = hobli_obj.get('id')
    print('area->',area_og)
    print("hob_id->",hobli_id)
    direction_id = get_direction(hobli_id)
    city_id = '806016000001466539'
    #Make a api call to update the area city direction and hobli
    zoho_url = "https://www.zohoapis.in/crm/v2/Accounts"
    header = {
        'Authorization':os.getenv('ZOHO_ACCESS_TOKEN')
    }
    payload =  {
  "data": [
    {
      "id": acc_id, 
      "Area1": area_og,
      "Hobli":hobli_id,
      "Direction":direction_id,
      "City":city_id
    }
  ]
}
    
    try:
        response = requests.put(url=zoho_url,headers=header,json=payload,verify=True)
        print("update response->",response.json())
    except Exception as e:
        print("Error happened while updating")
     
def get_accounts():
    zoho_url = "https://www.zohoapis.in/crm/v2/Accounts?page=2&per_page=10"
    header = {
        'Authorization':os.getenv('ZOHO_ACCESS_TOKEN')
    }
    try:
        response = requests.get(url=zoho_url,headers=header,verify=True)
        response.raise_for_status()
        data = response.json()
        data_array = data.get('data')
        for acc in data_array:
         area = acc.get('Area')
         acc_id = acc.get('id')
         pass
         area_obj = check_area_with_crm(area=area)
         print(area_obj)
        #  if area_obj:
        #      update_accounts(area_obj,acc_id)
        # print()
    except Exception as e:
        print(e)

get_accounts()

# zoho_url_city = "https://www.zohoapis.in/crm/v2/Direction/search?criteria=id:equals:806016000001505173"
# header = {
#         'Authorization':os.getenv('ZOHO_ACCESS_TOKEN')
#     }
# direction_res = requests.get(url=zoho_url_city,headers=header,verify=True)
# print(direction_res.json())







