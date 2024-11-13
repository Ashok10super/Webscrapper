from flask import Flask, request, send_file
import requests
import openpyxl
from io import BytesIO
from flask_cors import CORS
from bs4 import BeautifulSoup  # importing beauttiful soup module
import pandas as pd  # importing pandas for creating excel file

app = Flask(__name__)
# Import CORS
# CORS(app)
CORS(app, resources={r"/generate-excel": {"origins": "http://127.0.0.1:5501"}})


@app.route("/generate-excel", methods=["POST"])
def generate_excel():
    data = request.json

    Auction_id = data["auctionId"]
    if Auction_id == "":
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


def scrapperwithAuctionid():
    return 0


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

    url = (
        "https://www.eauctionsindia.com/search?auction=&order=&keyword=&category="
        + "&state="
        + state
        + "&city="
        + city
        + "&bank="
        + bank
        + "+Bank&min_price="
        + minPrice
        + "&max_price="
        + maxPrice
        + "&from="
        + auctionStartDate
        + "&to="
        + auctionEndDate
    )
    # print(url)
    print("Base url->", url)
    response = requests.get(url)
    if response.status_code != 200:
        print("Fetching unsuccess")
        return "Failed targeted website is down"
    soup = BeautifulSoup(response.text, "html.parser")
    # print(soup)
    target_divs = soup.findAll(
        "div",
        class_="odd:bg-white even:bg-pc2 odd:text-black p-4 rounded-lg shadow-pgbtn my-4",
    )  # getting all the links
    # print("targetd links->", target_divs)  # print all the links on the page

    # print("Next url", next_url["href"])
    # if target_next_page and "href" in target_next_page.attrs:
    #     print("Next page link:", target_next_page["href"])
    # else:
    #     print("Next page link not found or href attribute is missing.")
    link = []

    for div in target_divs:
        link_tag = div.find("a")
        if link_tag and "href" in link_tag.attrs:
            auction_link = link_tag["href"]
            link.append(auction_link)
        else:
            print("No link found.")

    return vist_and_construct_excel(link, area, SubmissionLastDate, category)
    # for div in target_divs:
    #   p_tag = div.find()  # Find the first <p> tag in the current <div>
    # if p_tag is not None:
    #     p_tags.append(p_tag)  # Add the <pauction_data_dict[td_data[i].get_text()] = td_data[i + 1].get_text()


def vist_and_construct_excel(link, area, submissionLastDate, category):
    # print(link)
    properties_list = []  # Stores all the properties in a list of dict
    print("This is links->", link)
    for url in link:
        response = requests.get(url)
        if response.status_code != 200:
            return "Targeted website is down"

        soup = BeautifulSoup(response.text, "html.parser")
        full_details = soup.find(class_="col-lg-12 col-md-12 col-sm-12 p-2")

        # Extract Auction ID (Look for the first <span> inside the first <p> tag)
        Auction_id = soup.find("div", class_="auction-block").find("p").get_text()

        Row = soup.find("div", class_="bank-details row")  # Bank html block extraction

        bank_name = Row.find("a", class_="color-highlight").text.strip()

        # Extracting EMD
        emd = Row.find_all("h6")[0].text.split(":")[1].strip()

        # Extracting Branch Name
        branch_name = Row.find_all("h6")[1].text.split(":")[1].strip()

        # Extracting Service Provider
        service_provider = Row.find_all("h6")[2].text.split(":")[1].strip()

        # Extracting Reserve Price
        reserve_price_element = soup.find(
            "div", class_="col-sm-6 reserve-price pt-3"
        ).find("span")
        if reserve_price_element:
            reserve_price = reserve_price_element.get_text()

        else:
            print("Reserve Price not found")

        # Extracting Contact Details
        contact_details = Row.find("p", class_="color-highlight").text.strip()

        discription_block = soup.find("div", class_="description-block")

        disp = discription_block.find("p")

        # Extracting the State and city using a tag inside dicription block
        Hold_location = list()
        get_city_area_state = discription_block.find_all("span")

        for item in get_city_area_state:
            Hold_location.append(item.get_text())

        Hold_location[1] = Hold_location[1].strip()
        state = Hold_location[0]

        city = Hold_location[1]

        property_area = Hold_location[2]

        # Extract the the property details
        property_details = soup.find("div", class_="property-details-block")
        property = list()
        details = property_details.find_all("h6")
        for span in details:
            property.append(span.get_text())

        cleaned_list = [
            item.replace(":", "").replace("\n", "").replace("\xa0", "").strip()
            for item in property
        ]

        borrower_name = cleaned_list[0]

        asset_category = cleaned_list[1]

        property_type = cleaned_list[2]

        auction_type = cleaned_list[3]

        auction_start_time = cleaned_list[4]

        auction_end_time = cleaned_list[5]

        application_submissionLastDate = cleaned_list[6]
        # Check the input area and category matches with the fetched data
        isvalidated = validate_area_category(
            area, property_area, category, asset_category
        )
        print(isvalidated)
        if isvalidated:
            properties_list.append(
                construct_dict(
                    auction_id=Auction_id,
                    bank_name=bank_name,
                    emd=emd,
                    branch_name=branch_name,
                    service_provider=service_provider,
                    reserve_price=reserve_price,
                    contact_details=contact_details,
                    discription=disp,
                    state=state,
                    city=city,
                    area=property_area,
                    borrower_name=borrower_name,
                    asset_category=asset_category,
                    property_type=property_type,
                    auction_type=auction_type,
                    auction_start=auction_start_time,
                    auction_end=auction_end_time,
                    sub_end=application_submissionLastDate,
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
):

    temp_dict = {
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
    }

    return temp_dict


def validate_area_category(area, property_area, category, asset_category):
    cap_area = ""
    if area != "":
        cap_area = area.capitalize()
    if cap_area == "" and category == "":
        return True
    elif cap_area == property_area and category == "":
        return True
    elif category == asset_category and cap_area == "":
        return True
    elif category == asset_category and cap_area == property_area:
        return True
    else:
        return False


def construct_excel(properties):
    df = pd.DataFrame(properties)

    # Save the DataFrame to an Excel file
    excel_file_path = "property.xlsx"
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False)  # Save the DataFrame to the in-memory buffer
    excel_file.seek(0)  # Reset the buffer to the beginning

    # Return the in-memory Excel file (BytesIO object)
    return excel_file


if __name__ == "__main__":
    app.run(port=8080)
