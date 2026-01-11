import requests
from bs4 import BeautifulSoup  # importing beauttiful soup module
from datetime import datetime,date
from pymongo.errors import DuplicateKeyError
from requests.sessions import HTTPAdapter
from urllib3 import Retry
from eauctionsindiabot.image_extractor.imageextract import extract_text
from eauctionsindiabot.gemini_api.gemini import get_outstanding
from eauctionsindiabot.service.property_service import is_property_already_there  #database connection and its operations
from eauctionsindiabot.utils.utlis import get_auction_id
from eauctionsindiabot.custom_exceptions.exceptions import StartScrapperError, SingleScrapperError, DatabaseError
from eauctionsindiabot.utils.utlis import sale_notice_url_formatter

#one tcp/ip 3-way handshake is made to the server and using the instance we are making repeated requests
session = requests.session()
headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Referer": "https://www.eauctionsindia.org/",
        "Cookie": "wssplashchk=99bcfb9ff292e9266b65b56e677553d7bf326f02.1754305132.1"
    }
session.headers.update(headers)
retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))

def start_scrapping(state,date,conn):

    url = f'https://www.eauctionsindia.com/search?keyword=&category=residential&state={state}&city=&area=&bank=&from={date}&to=&min_price=&max_price='
    link = [] #stores all the links from the pagination
    # create a session for connection pooling
    # print(url)
    print("Base url->", url)
    try:
        response = session.get(url, timeout=45)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        raise StartScrapperError(e) from e

    # Check response status
    if response.status_code == 200:
        print("Fetching success")
        soup = BeautifulSoup(response.text, "html.parser")
    else:
        print("Unexpected status code:", response.status_code)
        raise StartScrapperError("The status code was not 200",response.status_code)
    # check for the pagination
    pagination = soup.find("ul", class_="pagination")
    print("pagination", pagination)
    if pagination != None:
        last_page_link = pagination.find_all("a", class_="page-item page-link")[-1]
        last_number = int(last_page_link.text)
        print("This is the last number->",last_number)
        for page in range(1, last_number):
            url = f'https://www.eauctionsindia.com/search/{page}?category=residential&state={state}&from={date}'
            print("This is the pagination url", url)
            try:
                response = session.get(url=url, timeout=45)
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                raise StartScrapperError(e) from e
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                contanier_div = soup.findAll("div", class_="row mb-3")
                for i in contanier_div:
                    auction_link_temp = i.find("div",class_="col-lg-9 col-md-9 col-sm-12 col-xs-12")
                    if auction_link_temp is not None:
                        auction_link = auction_link_temp.find_all("div",class_="row")[-1]
                        auction_links = (auction_link.find("a")["href"])
                        print("auction link->",auction_links)
                        auction_id = get_auction_id(auction_links)#extracts the auction_id from the url
                        if is_property_already_there(auctionid=auction_id,coll=conn):
                         print("property already there=>",auction_id)
                         continue
                        else:
                          url = "https://www.eauctionsindia.com" + str(auction_links)
                          link.append(url)
            # for div in target_divs:
            #     link_tag = div.find("a")
            #     if link_tag and "href" in link_tag.attrs:
            #         auction_link = link_tag["href"]
            #         print("auction_link", auction_link)
            #         url = "https://www.eauctionsindia.com" + str(auction_link)
            #         link.append(url)
            from eauctionsindiabot.config import log_check_list,Status
            log_check_list["start_scrapper_info"]["status"] = Status.SUCCESS
        return vist_and_save_to_db(
            link,conn
        )
    else: #if- pagination is none then else block will execute
        response = session.get(url=url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            target_divs = soup.findAll("div", class_="ms-auto")
        for div in target_divs:
            link_tag = div.find("a")
            if link_tag and "href" in link_tag.attrs:
                auction_link = link_tag["href"]
                print("auction_link", auction_link)
                url = "https://www.eauctionsindia.com" + str(auction_link)
                link.append(url)
        return vist_and_save_to_db(link,conn)


def vist_and_save_to_db(link,conn):
    print('New properties List->',link)
    total_new_properties = len(link)
    properties_list = []  # Stores all the properties in a list of dict
    properties_sale_notice_linkstext = dict()
    print("Total number of properties",total_new_properties)
    i=0 # iteration flag
    for url in link:
        i=i+1
        print("No of iteration ->",i)
        try:
            response = session.get(url, timeout=60)
            if response.status_code != 200:
             print("Targeted url page is down so continue to next url",response.status_code)
             continue
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            raise SingleScrapperError(e) from e

        from eauctionsindiabot.config import log_check_list, Status
        log_check_list["single_scrapper_info"]["status"] = Status.SUCCESS
        soup = BeautifulSoup(response.text, "html.parser")
        auction_id_class = soup.find(class_="text-dark fw-bold")
        print("Auction_id", auction_id_class)

        # Extract Auction ID (Look for the first <span> inside the first <p> tag)

        auction_text = auction_id_class.get_text(strip=True)
        Auction_id = auction_text.split("#")[-1].strip()

        bank_name_element = soup.find("strong", text="Bank Name : ").find_next_sibling(
            "span"
        )
        bank_name = (
            bank_name_element.get_text(strip=True) if bank_name_element else None
        )

        # Extract EMD
        emd_element = soup.find("strong", text="EMD : ")
        if(emd_element!=None):
            emd_element=emd_element.find_next_sibling('span')
        emd = (
            emd_element.get_text(strip=True).replace("₹", " ").strip()
            if emd_element
            else None
        )
        # Extract Branch Name
        branch_name_element = soup.find(
            "strong", text="Branch Name : "
        ).find_next_sibling("span")
        branch_name = (
            branch_name_element.get_text(strip=True) if branch_name_element else None
        )

        # Extract Service Provider
        service_provider_element = soup.find(
            "strong", text="Service Provider : "
        ).find_next_sibling("span")
        service_provider = (
            service_provider_element.get_text(strip=True)
            if service_provider_element
            else None
        )

        # Extract Reserve Price
        reserve_price_element = soup.find(
            "strong", text="Reserve Price : "
        ).find_next_sibling("span")
        reserve_price = (
            reserve_price_element.get_text(strip=True).replace("₹", " ").strip()
            if reserve_price_element
            else None
        )

        # Extract Contact Details
        contact_details_element = soup.find(
            "strong", text="Contact Details : "
        ).find_next("p")
        contact_details = (
            contact_details_element.get_text(strip=True)
            if contact_details_element
            else None
        )

        # Extract Description
        description_div = soup.find_all("div", class_="mb-4")
        description = description_div[5]
        description_text = (
            description.find("p").text if description.find("p") else "No <p> tag found"
        )
        print("Description", description_text)
       
        # Extract State
        state_element = soup.find("strong", text="Province/State : ").find_next("a")
        state = state_element.get_text(strip=True) if state_element else None

        # Extract City
        city_element = soup.find("strong", text="City/Town : ").find_next("a")
        city = city_element.get_text(strip=True) if city_element else None

        # Extract Area
        area_element = soup.find("strong", text="Area/Town : ").find_next("span")
        areas = area_element.get_text(strip=True) if area_element else None

        # hobli  = area_and_hobli(description=description_text) 

        # Extract Borrower Name
        borrower_name_element = soup.find(
            "strong", text="Borrower Name : "
        ).find_next_sibling("span")
        borrower_name = (
            borrower_name_element.get_text(strip=True)
            if borrower_name_element
            else None
        )

        # Extract Asset Category
        asset_category_element = soup.find(
            "strong", text="Asset Category : "
        ).find_next("a")
        asset_category = (
            asset_category_element.get_text(strip=True)
            if asset_category_element
            else None
        )

        # Extract Property Type
        property_type_element = soup.find(
            "strong", text="Property Type : "
        ).find_next_sibling("span")
        property_type = (
            property_type_element.get_text(strip=True)
            if property_type_element
            else None
        )

        # Extract Auction Type
        auction_type_element = soup.find(
            "strong", text="Auction Type : "
        ).find_next_sibling("span")
        auction_type = (
            auction_type_element.get_text(strip=True) if auction_type_element else None
        )

        # Extract Auction Start Time
        auction_start_element = soup.find(
            "strong", text="Auction Start Date : "
        ).find_next_sibling("span")
        auction_start = (
            auction_start_element.get_text(strip=True)
            if auction_start_element
            else None
        )
        if auction_start:
            auction_start_date = datetime.strptime(auction_start, '%d-%m-%Y %I:%M %p')
        # Extract Auction End Time
        auction_end_element = soup.find(
            "strong", text="Auction End Time : "
        ).find_next_sibling("span")
        auction_end = (
            auction_end_element.get_text(strip=True) if auction_end_element else None
        )
        if auction_end:
            auction_end_date = datetime.strptime(auction_end,'%d-%m-%Y %I:%M %p')
        # Extract Application Submission End Date
        sub_end_element = soup.find(
            "strong", text="Application Subbmision Date : "
        ).find_next_sibling("span")
        sub_end = sub_end_element.get_text(strip=True) if sub_end_element else None

        # Extract Sale Notice URL
        sale_notice_element = soup.find("strong", text="Sale Notice 1: ")
        print("Sale notice element", sale_notice_element)
        sale_notice_url = ''
        if sale_notice_element:
            sale_notice_element = sale_notice_element.find_next_sibling("span").find("a")
            sale_notice_url = sale_notice_element.get("href", "").strip()

        # -------- Case: No sale notice link ----------
        if not sale_notice_url:
            print("No sale notice link found")
            outstanding_amount = ""  # nothing to extract

        # -------- Case: PDF sale notice ----------
        elif sale_notice_url.lower().endswith(".pdf"):
            print("Sale notice is PDF – skipping extraction")
            outstanding_amount = ""  # skip Gemini, but keep PDF link

        # -------- Case: HTML sale notice ----------
        else:
            if sale_notice_url in properties_sale_notice_linkstext:
                print("Sale notice already cached")
                text = properties_sale_notice_linkstext[sale_notice_url]
            else:
                print("Fetching sale notice text")
                formatted_notice_url = sale_notice_url_formatter(sale_notice_url)
                text = extract_text(formatted_notice_url, session)
                properties_sale_notice_linkstext[sale_notice_url] = text

            print("Sending to Gemini")
            outstanding_amount = get_outstanding(
                text=text,
                borrower_name=borrower_name,
                emd=emd
            )
        today = date.today()
        today_dt = datetime.combine(today, datetime.min.time())
        constructed_dict = construct_dict(
                auction_id=Auction_id,
                bank_name=bank_name,
                emd=emd,
                branch_name=branch_name,
                service_provider=service_provider,
                reserve_price=reserve_price,
                contact_details=contact_details,
                description=description_text,
                state=state,
                city=city,
                area=areas,
                borrower_name=borrower_name,
                asset_category=asset_category,
                property_type=property_type,
                auction_type=auction_type,
                auction_start_date=auction_start_date,
                auction_end_date=auction_end_date,
                sub_end=sub_end,
                sale_notice=sale_notice_url,
                outstanding_amount=outstanding_amount,
                fetch_date = today_dt
            )
        #push the extracted details to the mongodb
        try:
            conn.insert_one(constructed_dict)
            print("inserted into collection successfully")
        except DuplicateKeyError:
            # This is NOT an error. It's expected behavior.
            print(f"Auction ID already exists. Skipping.")
            pass  # Just ignore it and continue
        except Exception as e:
            print("Error raised at single property insertion",e)
            raise DatabaseError(f"Database connection failed: {e}") from e
        properties_list.append(constructed_dict)
    print("This is properties list :", properties_list)
    print("Total number of new properties->",len(properties_list))
    from eauctionsindiabot.config import log_check_list,Status
    log_check_list["gemini_api_info"]["status"] = Status.SUCCESS
    log_check_list["tesseract_ocr_info"]["status"] = Status.SUCCESS
    return len(properties_list)

def construct_dict(
    auction_id,
    bank_name,
    emd,
    branch_name,
    service_provider,
    reserve_price,
    contact_details,
    description,
    state,
    city,
    area,
    borrower_name,
    asset_category,
    property_type,
    auction_type,
    auction_start_date,
    auction_end_date,
    sub_end,
    sale_notice,
    outstanding_amount,
    fetch_date
):
    temp_dict = {
        "Account name": auction_id + "-" + bank_name + "-",
        "Auction Id": auction_id,
        "Bank Name": bank_name,
        "EMD": emd,
        "Branch Name": branch_name,
        "Service Provider": service_provider,
        "Reserve Price": reserve_price,
        "Contact Details": contact_details,
        "Description": description,  # Ensure correct spelling
        "State": state,
        "City": city,
        "Area": area,
        "Borrower Name": borrower_name,
        "AssetCategory": asset_category,
        "Property Type": property_type,
        "Auction Type": auction_type,
        "auction_start_date": auction_start_date,
        "auction_end_date": auction_end_date,
        "Sub End": sub_end,
        "sale_notice": sale_notice,
        "outstanding_amount":outstanding_amount,
        "fetch_date": fetch_date
    }

    return temp_dict

