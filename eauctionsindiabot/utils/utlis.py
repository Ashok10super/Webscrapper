def get_auction_id(url:str):
    splited_url = url.split("/")
    auction_id  = splited_url[2]
    return auction_id