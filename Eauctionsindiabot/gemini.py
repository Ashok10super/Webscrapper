import requests
import json
api_key = "AIzaSyAs0f5cGePHI9qEjZWK2aju5umBQTTY-YM"

def get_outstanding(text,borrower_name):
    url ="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key="+api_key
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {"parts": [{"text": text+" "+borrower_name+" so the text contains the borrower details and the property details associated with the borrower"
            " so carefully read the text and find the outstanding amount and posession type of the property and give only two fields and value like this {outsanding_amount:"",possession_type:""}"}]}
        ]
    }
         
    
    try:
        response = requests.post(url=url,headers=headers,data=json.dumps(data))
        data = response.json()
        print(data)
        candidates = data['candidates']
        print(candidates)
        content = candidates[0]
        print(content)
        parts = content['content']
        texts = parts['parts']
        og_data = (texts[0])['text']
        print(og_data)
        return og_data
    except Exception as e:
        print(e)
