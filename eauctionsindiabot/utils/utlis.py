import re
def get_auction_id(url:str):
    pattern = r"https://www\.eauctionsindia\.com/properties/(\d+)"
    match = re.search(pattern=pattern,string=url)
    return match.group(1)


def sale_notice_url_formatter(sales_notice):
    if 'eauctionsindia' in sales_notice:
        return sales_notice
    else:
        return 'https://www.eauctionsindia.com'+sales_notice
