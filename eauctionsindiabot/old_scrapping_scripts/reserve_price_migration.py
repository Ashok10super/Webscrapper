from database import get_connection


def change_reserve_price():
    connection = get_connection()
    properties = connection.find({})
    counter = 0
    skipped = 0
    try:
        for prop in properties:
            old_rp = prop.get('Reserve Price')
            if old_rp is None or isinstance(old_rp, (int, float)):
                skipped += 1
                continue
            new_rp = float(str(old_rp).replace(",", "").strip())
            print(connection.update_one({"_id":prop['_id']},{'$set':{'Reserve Price':new_rp}}))
            counter += 1
            print(counter)
        print("Total number of docs migrated", counter )
        print("Total skipped docs migrated", skipped)
    except Exception as e:
        print("Error raised here",e)



change_reserve_price()

