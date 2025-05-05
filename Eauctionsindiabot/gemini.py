import requests
import json
api_key = "AIzaSyAs0f5cGePHI9qEjZWK2aju5umBQTTY-YM"

def get_outstanding(text,borrower_name,emd):
    url ="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key="+api_key
    headers = {"Content-Type": "application/json"}
    data = {
            "contents": [
                {"parts": [{"text": text+" "+borrower_name+" so the text contains the borrower details and the property details associated with the borrower"
                f" so carefully read the text and undertand the context of the salenotice text then find the outstanding amount if the outstanding amount is equal to {emd} then the outstanding amount is wrong recheck it might in differnt words like demand notice amount once you"
                "once found give it in json format only outstanding amount like this only one outstanding amount not more than one {outstanding :""} don't ever change the outstanding amount format otherwise my code will break"}]}
            ]
        } 
    
    try:
        response = requests.post(url=url,headers=headers,data=json.dumps(data))
        data = response.json()
        print(data)
        candidates = data['candidates']
        print(candidates)
        content = candidates[0]
        parts = content['content']
        texts = parts['parts']
        og_data = (texts[0])['text']
        print(og_data)
        json_string = og_data.strip("```json/n").strip("/n```")
        value = json.loads(json_string)
        print(value)
        return value['outstanding']
    except Exception as e:
        print(e)

def area_and_hobli(description):
    url ="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key="+api_key
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {"parts": [{"text":description+"extract the hobli from the text give it in this format if not found null{hobbli:""}"
            }]}
        ]
    }
    try:
        response = requests.post(url=url,headers=headers,data=json.dumps(data))
        data = response.json()
        candidates = data['candidates']
        print(candidates)
        content = candidates[0]
        print(content)
        parts = content['content']
        texts = parts['parts']
        og_data = (texts[0])['text']
        print("Hobli and direcion",og_data)
        return og_data
    except Exception as e:
        print(e)
        
