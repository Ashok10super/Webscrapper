import requests
from bs4 import BeautifulSoup
from Eauctionsindiabot.Bot import vist_and_construct_excel


def url():
    url = "https://www.eauctionsindia.com/search/2?auction=&keyword=&category=residential&state=karnataka&city=bengaluru&bank=&from=2024-12-14&to=&min_price=&max_price=&order="
    response = requests.get(url)
    if response.status_code != 200:
        print("Fetching unsuccess")
        return "Failed targeted website is down"
    soup = BeautifulSoup(response.text, "html.parser")
    # print(soup)

    target_divs = soup.findAll(
        "div",
        class_="col-sm-12 col-md-6 col-lg-6 d-lg-flex justify-content-end",
    )
    link = []

    print("Targeted divs", target_divs)
    for div in target_divs:
        link_tag = div.find("a")
        if link_tag and "href" in link_tag.attrs:
            auction_link = link_tag["href"]
            link.append(auction_link)
        else:
            print("No link found.")

    print(link)
    excel_buffer = vist_and_construct_excel(link=link, area="", submissionLastDate="")
    with open("properties.xlsx", "wb") as f:
        f.write(excel_buffer.getvalue())

        # Optional: Close the buffer
        excel_buffer.close()
    print("Excel file has been saved as 'property.xlsx'")


url()
