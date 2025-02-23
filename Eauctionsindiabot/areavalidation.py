import os
import dotenv 
dotenv.load_dotenv()
import requests


api_key = os.getenv("GEMINI_KEY")

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key="+api_key
headers ={
    'Content-Type' : 'application/json'
}
areas = ['Kengeri','MG Road','Kodigehalli','Koramangala','DEVARAJEEVANAHALL']
for area in areas: 
   try:
    payload ={
        "contents": [{
        "parts":[{"text": area+" is in which hobli and which direction and which city in bengaluru give the answer in this format city,direction,hobli search hobli deeply and give answers"}]
        }]
    }
    gemini = requests.post(url=url,headers=headers,json=payload,).json()
    og_text_ai = (gemini['candidates'])[0]
    og_content = og_text_ai.get('content').get("parts")[0]
    og_text = og_content.get('text')
    print(og_text)
   except Exception as e:
     gemini_response = requests.post(url=url,payload={
       "contents":[{"Parts":[{"text":str(e)}]}]})
     print(gemini_response)
     

