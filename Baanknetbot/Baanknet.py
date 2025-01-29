import requests
import pandas as pd
# import sys
# sys.path.append('/home/ashok/scrapper/Eauctionsindiabot/Bot.py')
# from Eauctionsindiabot.Bot import construct_excel

session = requests.session()

# API URL and payload


def get_total_property_list():
    url = "https://baanknet.com/eauction-psb/api/property-listing-data/1?page=0&size=10"
    payload = {
        "city": "Bengaluru",
        "priceFrom": "0",
        "sortBy": "3",
        "priceTo": "1000000000",
    }

    headers = {"Content-Type": "application/json"}

    # Step 1: Fetch data from API
    response = session.post(url=url, json=payload, headers=headers, verify=False)

    if response.status_code == 200:
        print("Request successful")
        data = response.json()  # Convert JSON response to Python dictionary
        print("Total count->", data["totalCount"])
        get_propId(
            total_prop_count=data["totalCount"],
            url=url,
            payload=payload,
            headers=headers,
        )


def get_propId(total_prop_count, url, payload, headers):

    # total_prop count is the total number of properties available for the fetch cobert the varible from int to str
    # url is the same but we need to change the query parameter size to total_prop_count
    new_url = url.replace("10", str(total_prop_count))
    print("This is the new url after updation->", new_url)
    propertyId_list = []
  # list stores all the property_id that is fetcched from the api call

    try:
        response = session.post(
            url=new_url, verify=False, json=payload, headers=headers
        )  # call the api to get all the propertyId
        if response.status_code == 200:
            data = response.json()  # loads the json response and converts it into dict
            array_property_id = data['data']#get the array of properties
            count=0

            for property in array_property_id:#get all the property_id and store those id's in the list
                print(property['propertyId'])
                count=count+1
                propertyId_list.append(property['propertyId'])

        print(count==total_prop_count) 


    except requests.exceptions.RequestException as e:
        print("Error while calling the api ->", e)


    fetch_property_details(propId_list=propertyId_list,headers=headers)#calling fetch_property_details to respond back with the fetched data


def fetch_property_details(propId_list,headers):
    property_list = []
    for prop in propId_list:
        prop_url = "https://baanknet.com/eauction-psb/api/view-property-detail/"+str(prop)+"/1"
        print(prop_url)
        response_data = session.get(url=prop_url, verify=False, headers=headers)
        try:
            if response_data.status_code == 200:
                #list to store all the property_details dict

                data = response_data.json()
                resp_data = data.get('respData', {})
                print(resp_data)
              
                auction_details = resp_data.get('auctionDetails', {}) or {}
                print("Auction_id->", auction_details)
                

                Auction_id = auction_details.get('AuctionId')
                print("Auction id->", Auction_id if Auction_id is not None else "Not Available")

                Emd = auction_details.get('EMD')
                print("EMD amount->", Emd if Emd is not None else "Not Available")

                Reserve_price = auction_details.get('ReservePrice')
                print("Reserve price->", Reserve_price if Reserve_price is not None else "Not Available")

                Auction_start_date = auction_details.get('Auctionstartdate')
                print("Auction start date->", Auction_start_date if Auction_start_date is not None else "Not Available")

                Auction_end_date = auction_details.get('AuctionEndDate')
                print("Auction end date->", Auction_end_date if Auction_end_date is not None else "Not Available")

                Bankname = resp_data.get('bankName')
                print("Bank name->", Bankname if Bankname is not None else "Not Available")

                Branchname = resp_data.get('locality')
                print("Branch name->", Branchname if Branchname is not None else "Not Available")

                City = resp_data.get('city')
                print("City->", City if City is not None else "Not Available")

                Area = resp_data.get('locality')
                print("Area->", Area if Area is not None else "Not Available")

                state_info = resp_data.get('commonPropertyDetails', {}).get('stateId', {})
                State = state_info.get('stateName')
                print("State->", State if State is not None else "Not Available")

                Service_provider = "Ebkray"

                Contact_details = resp_data.get('commonPropertyDetails', {}).get('department', {}).get('phoneNo')
                print("Contact details->", Contact_details if Contact_details is not None else "Not Available")

                Description = resp_data.get('commonPropertyDetails', {}).get('summaryDesc')
                print("Description->", Description if Description is not None else "Not Available")

                Borrower_name = resp_data.get('commonPropertyDetails', {}).get('borrowerName')
                print("Borrower name->", Borrower_name if Borrower_name is not None else "Not Available")

                property_type_info = resp_data.get('commonPropertyDetails', {}).get('propertySubType', {})
                Property_type = property_type_info.get('propertySubType')
                print("Property type->", Property_type if Property_type is not None else "Not Available")
                

                possession = resp_data.get('commonPropertyDetails',{}).get('propertyPossessionTypeId',{}).get('propertyPossessionType')
                possession if possession is not None else "Not Available"

                Auction_type = 'Sarfaesi Auction'

                Sale_notice_link = "https://baanknet.com/eauction-psb/api/download-property-document/"+str(prop)

                #After fetching all the nescesssary datas create a dict and store that dict to the list
                property_list.append(construct_dict(auction_id=Auction_id,bank_name=Bankname,emd=Emd,branch_name=Branchname,service_provider=Service_provider,
                            reserve_price=Reserve_price,contact_details=Contact_details,discription=Description,state=State,city=City,
                            area=Area,borrower_name=Borrower_name,asset_category="None",property_type=Property_type,auction_type=Auction_type,
                            auction_start=Auction_start_date,auction_end=Auction_start_date,sub_end="None",sale_notice=Sale_notice_link,Possession_type=possession))
                print("Latest_prop_list",property_list)
   
        except requests.exceptions.RequestException as e:
            print("Error happend while making api call->",e) 

    print(property_list)    
    create_excel(prop_list=property_list)



def create_excel(prop_list):
    try:
        df = pd.DataFrame(prop_list)
        df.to_excel('/home/ashok/scrapper/Baanknetbot/Baanknetextract.xlsx',index=False)
        print("Excel successfully created")
    except Exception as e:
        print(e)    
#strating point of the execution
def construct_dict(
    auction_id,
    bank_name,
    emd,
    branch_name,
    service_provider,
    reserve_price,
    contact_details,
    discription,
    state,
    city,
    area,
    borrower_name,
    asset_category,
    property_type,
    auction_type,
    auction_start,
    auction_end,
    sub_end,
    sale_notice,
    Possession_type,
):
    temp_dict = {
        "Account name": str(auction_id) + "-" + str(bank_name) + "-",
        "Auction Id": auction_id,
        "Bank Name": bank_name,
        "EMD": emd,
        "Branch Name": branch_name,
        "Service Provider": service_provider,
        "Reserve Price": reserve_price,
        "Contact Details": contact_details,
        "Description": discription,  # Ensure correct spelling
        "State": state,
        "City": city,
        "Area": area,
        "Borrower Name": borrower_name,
        "Asset Category": asset_category,
        "Property Type": property_type,
        "Auction Type": auction_type,
        "Auction Start": auction_start,
        "Auction End": auction_end,
        "Sub End": sub_end,
        "sale_notice": sale_notice,
        "Possession_type":Possession_type,
    }

    return temp_dict
get_total_property_list()
