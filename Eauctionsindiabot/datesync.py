import database
from datetime import datetime


def update_old_property_by_date():
     coll = database.get_connection()
     docs =   coll.find()
     input_date = datetime.strptime("1-05-2025 02:00 PM","%d-%m-%Y %I:%M %p")
     for doc in docs:
        date = doc['Auction Start']
        formated_date = datetime.strptime(date,"%d-%m-%Y %I:%M %p")
        if formated_date>input_date:
            coll.update_one({"_id":doc['_id']},{
                "$set":{"property_status":"New"}},upsert=False)
            print("doc updated successfully as New")
        else:
            coll.update_one({"_id":doc['_id']},{
                "$set":{"property_status":"old"}},upsert=False)
            print("doc updated as old")
                  
    
update_old_property_by_date()