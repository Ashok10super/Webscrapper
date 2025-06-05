import database
from datetime import datetime



def clear_today_dB():
    try:
         database.get_today_coll().delete_many({})
    except Exception as e:
        print("unable to delete the day collection",e)   

def update_old_property_by_date():
     flag=0
     coll = database.get_connection()
     docs =   coll.find({})
     input_date = datetime.strptime("19-05-2025 10:00 AM","%d-%m-%Y %I:%M %p")
     for doc in docs:
        date = doc['Auction Start']
        formated_date = datetime.strptime(date,"%d-%m-%Y %I:%M %p")
        if formated_date>input_date:
            pass
        else:
            flag+=1
            coll.update_one({"_id":doc['_id']},{
                "$set":{"property_status":"Expired"}},upsert=False)
            print("doc updated as expired")
     print("Total expired properties",flag)              
    
clear_today_dB()
