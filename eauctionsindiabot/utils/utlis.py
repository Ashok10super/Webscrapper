def get_auction_id(url:str):
    splited_url = url.split("/")
    auction_id  = splited_url[2]
    return auction_id


def sale_notice_url_formatter(sales_notice):
    if 'eauctionsindia' in sales_notice:
        return sales_notice
    else:
        return 'https://www.eauctionsindia.com'+sales_notice
