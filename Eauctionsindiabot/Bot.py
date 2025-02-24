from flask import Flask, request, send_file
import requests
from io import BytesIO
from flask_cors import CORS
from bs4 import BeautifulSoup  # importing beauttiful soup module
import pandas as pd  # importing pandas for creating excel file
from datetime import datetime  # importing datetime object to format the date


app = Flask(__name__)
# Import CORS
# CORS(app)
CORS(app, resources={r"/generate-excel": {"origins": "http://127.0.0.1:5501"}})

#one tcp/ip 3-way handshake is made to the server and using the instance we are making repeated
session = requests.session()


@app.route("/generate-excel", methods=["POST"])
def generate_excel():
    data = request.json

    Auction_id = data["auctionId"]
    if Auction_id == "":
        # check the total number of properties
        excel_file = scrapperwithoutAuctionId(data)
    # print(data.AuctionId)

    # Create a new Excel workbook in memory

    # Send the file as a downloadable attachment  file_name = +'property.xlsx'

    return send_file(
        excel_file,
        as_attachment=True,
        download_name="auction_data.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

def scrapperwithoutAuctionId(data):

    auction_id = None  # Auction id used to fetch details of request
    category = data["category"]  # Removed from the search list
    state = data["state"]
    city = data["city"]
    bank = data["bankName"]
    area = data[
        "area"
    ]  # This is additional information given by the user to filter out the properties
    maxPrice = data["maxPrice"]
    minPrice = data["minPrice"]
    auctionStartDate = data["auctionStartDate"]
    auctionEndDate = data["auctionEndDate"]
    SubmissionLastDate = [data["tenderLastDate"]]  # This is also a additional filed

    if category == "select-category":
        category = ""
    new_bank = bank.replace(" ", "+")
    print(new_bank)
    page = 1
    url = construct_url(
        page=page,
        category=category,
        state=state,
        city=city,
        new_bank=bank,
        min_price=minPrice,
        max_price=maxPrice,
        auctionStartDate=auctionStartDate,
        auctionEndDate=auctionEndDate,
    )
    link = []
    # create a session for connection pooling
    # print(url)
    print("Base url->", url)
    try:
        response = session.get(url, timeout=45)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    # Check response status
    if response.status_code == 200:
        print("Fetching success")
        soup = BeautifulSoup(response.text, "html.parser")

    else:
        print("Unexpected status code:", response.status_code)
    # check for the pagination
    pagination = soup.find("ul", class_="pagination")
    print("pagination", pagination)
    if pagination != None:
        last_page_link = pagination.find_all("a", class_="page-item page-link")[-1]
        last_number = int(last_page_link.text)
        print("This is the last number->",last_number)
        for page in range(1, last_number):
            url = construct_url(
                page=page,
                category=category,
                state=state,
                city=city,
                new_bank=bank,
                min_price=minPrice,
                max_price=maxPrice,
                auctionStartDate=auctionStartDate,
                auctionEndDate=auctionEndDate,
            )
            print("This is the pagination url", url)
            try:
                response = session.get(url=url, timeout=45)
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                contanier_div = soup.findAll("div", class_="row mb-3")
                for i in contanier_div:
                    auction_link_temp = i.find("div",class_="col-lg-9 col-md-9 col-sm-12 col-xs-12")
                    if auction_link_temp is not None:
                        auction_link = auction_link_temp.find_all("div",class_="row")[-1]
                        print("auction_link",auction_link)
                        auction_links = (auction_link.find("a")["href"])
                        print("auction link->",auction_links)
                        url = "https://www.eauctionsindia.com" + str(auction_links)
                        link.append(url)
            # for div in target_divs:
            #     link_tag = div.find("a")
            #     if link_tag and "href" in link_tag.attrs:
            #         auction_link = link_tag["href"]
            #         print("auction_link", auction_link)
            #         url = "https://www.eauctionsindia.com" + str(auction_link)
            #         link.append(url)   
        return vist_and_construct_excel(
            link,
            area,
        )
    else:
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
        return vist_and_construct_excel(link, area)

    # print("targetd links->", target_divs)  # print all the links on the page

    # print("Next url", next_url["href"])
    # if target_next_page and "href" in target_next_page.attrs:
    #     print("Next page link:", target_next_page["href"])
    # else:
    #     print("Next page link not found or href attribute is missing.")
    # store all the a tag
    # for div in target_divs:
    #   p_tag = div.find()  # Find the first <p> tag in the current <div>
    # if p_tag is not None:
    #     p_tags.append(p_tag)  # Add the <pauction_data_dict[td_data[i].get_text()] = td_data[i + 1].get_text()


def vist_and_construct_excel(
    link,
    area,
):
    print(link)
    properties_list = []  # Stores all the properties in a list of dict
    for url in link:
        try:
            response = session.get(url, timeout=45)
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
        if response.status_code != 200:
            print("Targeted website is down")
            return "Targeted website is down"

        soup = BeautifulSoup(response.text, "html.parser")
        auction_id_class = soup.find(class_="text-dark fw-bold")
        print("Auction_id", auction_id_class)

        # Extract Auction ID (Look for the first <span> inside the first <p> tag)

        auction_text = auction_id_class.get_text(strip=True)
        Auction_id = auction_text.split("#")[-1].strip()
        print(Auction_id)
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
        print("All the mb-4",description_div)
        description = description_div[5]
        print("Length of description->",len(description_div))
        print("Description-div->",description)
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

        # Extract Auction End Time
        auction_end_element = soup.find(
            "strong", text="Auction End Time : "
        ).find_next_sibling("span")
        auction_end = (
            auction_end_element.get_text(strip=True) if auction_end_element else None
        )

        # Extract Application Submission End Date
        sub_end_element = soup.find(
            "strong", text="Application Subbmision Date : "
        ).find_next_sibling("span")
        sub_end = sub_end_element.get_text(strip=True) if sub_end_element else None

        # Extract Sale Notice URL
        sale_notice_element = soup.find("strong", text="Sale Notice 1: ")
        print("Sale notice element", sale_notice_element)
        if sale_notice_element:
            sale_notice_element = sale_notice_element.find_next_sibling("span").find(
                "a"
            )
            temp_sales_notice = sale_notice_element["href"]
            if "eauctionsindia" in str(temp_sales_notice):
                print("Sale notice already contains link")
                sale_notice_url = temp_sales_notice
            else:
                sale_notice_url = (
                    "https://www.eauctionsindia.com" + sale_notice_element["href"]
                    if sale_notice_element
                    else ""
                )
        else:
            sale_notice_url = " "
        print("final sales notice url", sale_notice_url)
        print("Im done")
        properties_list.append(
            construct_dict(
                auction_id=Auction_id,
                bank_name=bank_name,
                emd=emd,
                branch_name=branch_name,
                service_provider=service_provider,
                reserve_price=reserve_price,
                contact_details=contact_details,
                discription=description_text,
                state=state,
                city=city,
                area=areas,
                borrower_name=borrower_name,
                asset_category=asset_category,
                property_type=property_type,
                auction_type=auction_type,
                auction_start=auction_start,
                auction_end=auction_end,
                sub_end=sub_end,
                sale_notice=sale_notice_url,
                Possession_type=""
            )
        )
    print("This is properties list :", properties_list)
    return construct_excel(properties=properties_list)


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
    auction_start,
    auction_end,
    sub_end,
    sale_notice,
    Possession_type,
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


def validate_area_category(area, property_area):
    cap_area = ""
    if area == "":
        return True
    else:
        cap_area = area.capitalize()
        return cap_area == property_area


def construct_excel(properties):
    df = pd.DataFrame(properties)
    # Save the DataFrame to an Excel file
    print("im from excel")
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False)  # Save the DataFrame to the in-memory buffer
    excel_file.seek(0)  # Reset the buffer to the beginning
    # Return the in-memory Excel file (BytesIO object)
    return excel_file


def format_date(date):
    date_time_obj = datetime.strptime(date, "%d-%m-%Y %I%M %p")
    formatted_date_time = date_time_obj.strftime("%d-%m-%Y %I:%M %p")
    return formatted_date_time

def construct_url(
    page,
    category,
    state,
    city,
    new_bank,
    min_price,
    max_price,
    auctionStartDate,
    auctionEndDate,
):
    url = (
        "https://www.eauctionsindia.com/search/"
        + str(page)
        + "?"
        + "&category="
        + category
        + "&state="
        + state
        + "&city="
        + city
        + "&bank="
        + new_bank
        + "+&min_price="
        + min_price
        + "&max_price="
        + max_price
        + "&from="
        + auctionStartDate
        + "&to="
        + auctionEndDate
    )
    return url


if __name__ == "__main__":
    app.run(port=8080)

