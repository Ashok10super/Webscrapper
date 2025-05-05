import pymongo


def get_connection():
    database_url = "mongodb+srv://developermybankauction:xlPPfXwtFjuOJ4vh@cluster0.j4zjk.mongodb.net/Zbot?retryWrites=true&w=majority&appName=Cluster0"
    try:
        conn  = pymongo.MongoClient(database_url)
        db = conn['Zbot']
        coll = db['Eauctionindia']
        return coll  
    except Exception as e:
        print(e)
        return e

def is_property_already_there(auctionid,coll):
    try:
        is_property_there = coll.find_one({'Auction Id':auctionid})
        print(is_property_there)
        if is_property_there!=None:
            return True
        else:
            return False
    except Exception as e:
        print(e)    
      
def update_the_prop_status(auction_id,coll):
    try:
        obj = coll.find_one_and_update({"Auction Id": auction_id},  # filter condition
        {"$set": {"property_status": "old"}},  # update operation
        return_document=True  # returns the updated document
        )
        if obj!=None:
            return "document updated"
        else:
            return "document not updated"
    except Exception as e:
        print(e)    

