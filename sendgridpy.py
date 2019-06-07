import os
import requests
import json

headers = {
    'content-type': 'application/json',
    'Authorization': 'Bearer ' + os.environ.get('SENDGRID_API_KEY')
    }

def send_email(from_email, recipient_email, user_name, veri_code):

    headers = {
    'content-type': 'application/json',
    'Authorization': 'Bearer ' + os.environ.get('SENDGRID_API_KEY')
    }
    
    api_url = 'https://api.sendgrid.com/v3/mail/send'

    payload = {

    "personalizations": [
     {
       "to": [
         {
           "email": recipient_email
         }
       ],
       "subject": "Verification Code From BayArt"
     }
    ],
    "from": {
     "email": from_email
    },
    "content": [
     {
       "type": "text/plain",
       "value": f"Hi {user_name}!\nYour verification code is {veri_code}."
     }
    ]
    }

    r = requests.post(api_url, data=json.dumps(payload), headers=headers)


# f"Hi {user_name}!\nYour verification code is {veri_code}."
# "Verification Code From BayArt."

def verify_email():
 api_url = 'https://api.sendgrid.com/v3/senders'

 payload = {
 "nickname": "Bay Art",
 "from": {
   "email": "bayareaartconnect@gmail.com",
   "name": "Bay Art"
 },
 "reply_to": {
   "email": "bayareaartconnect@gmail.com",
   "name": "Bay Art"
 },
 "address": "123 Elm St.",
 "address_2": "Apt. 456",
 "city": "Denver",
 "state": "Colorado",
 "zip": "80202",
 "country": "United States"
 }

 response = requests.post(api_url, data=json.dumps(payload), headers=headers)

 if response:
   print(response)