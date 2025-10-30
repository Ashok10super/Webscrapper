

def is_property_already_there(auctionid, coll):
    try:
        is_property_there = coll.find_one({'Auction Id': auctionid})
        if is_property_there != None:
            return True
        else:
            return False
    except Exception as e:
        print(e)


def update_the_prop_status(auction_id, coll):
    try:
        obj = coll.find_one_and_update({"Auction Id": auction_id},  # filter condition
                                       {"$set": {"property_status": "old"}},  # update operation
                                       return_document=True  # returns the updated document
                                       )
        if obj != None:
            return "document updated"
        else:
            return "document not updated"
    except Exception as e:
        print(e)


def delete_error_properties(coll):
    auction_id = [555966, 555965, 555979, 555976, 555569, 555560, 556050, 556047, 556045, 556032, 556031, 556030,
                  556029, 556028, 556027, 556026,
                  556025, 556024, 556023, 556022, 555113]

    print(len(auction_id))
    for i in auction_id:
        result = coll.find_one_and_delete({"Auction Id": str(i)})
        print(result)