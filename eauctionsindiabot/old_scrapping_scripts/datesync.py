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

def change_date_field():
    coll = database.get_connection()
    docs =   coll.find({})
    flag =0
    try:
        for doc in docs:
            if isinstance(doc['Auction Start'],str):
                auc_start_date = doc['Auction Start']
                print(type(auc_start_date))
                auction_start_formated_date = datetime.strptime(auc_start_date,"%d-%m-%Y %I:%M %p")
                auc_end_date = doc['Auction End']
                auction_end_formated = datetime.strptime(auc_end_date,"%d-%m-%Y %I:%M %p")
                coll.update_one({"_id":doc['_id']},{
                    "$set":{'Auction Start':auction_start_formated_date,
                            "Auction End": auction_end_formated}},upsert=False)
                flag+=1
            print("No documents updated->",flag)    
    except Exception as e:
        print("error->",e)
# clear_today_dB()
change_date_field()