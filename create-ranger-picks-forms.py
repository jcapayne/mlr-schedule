#!/usr/bin/env python3


# make sure we're running under the virtual environment
import os

my_path = os.path.abspath(os.path.dirname(__file__))

activate_this_file = "%s/bin/activate_this.py" % my_path

exec(open(activate_this_file).read(), {'__file__': activate_this_file})


from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests
import cssutils
from bs4 import BeautifulSoup
import sys
import traceback
import datetime
import json
from six.moves.html_parser import HTMLParser
from pprint import pprint
from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime, timedelta
import pytz
from pytz import timezone


# Path to your service account key JSON file
SERVICE_ACCOUNT_FILE = "%s/ranger-picks-d38ed51e8adc.json" % my_path

# Google Forms API and Sheets API scopes
SCOPES = [
    'https://www.googleapis.com/auth/forms.body',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',  
]

def create_form(round,matchups):
    # Authenticate using the service account
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    # Build the Forms and Sheets API clients
    forms_service = build('forms', 'v1', credentials=credentials)
    sheets_service = build('sheets', 'v4', credentials=credentials)
    drive_service = build('drive', 'v3', credentials=credentials)

    teams={
      "Anthem Rugby Carolina": { "image": "1tiMi6euXHc2Uw4IjkFCnzGd6zQLj9T_S", "short": "ARC" },
      "Chicago Hounds": { "image": "1X7nY6MNDYT3zNZxhmxaKlhbxDnxom8uW", "short": "CHI" },
      "Houston SaberCats": { "image": "1eIdehAde2eob3PceZg9nZ6vxhF4Z1H6H", "short": "HOU" },
      "Rugby LA": { "image": "1o5JgrSnBgt-cyZO6SZ0ZQ39lIO0L0qFO", "short": "RFCLA" },
      "Miami Sharks": { "image": "1UfZPgXhPbeupNZvcxr-MNMSDnrqsHAE2", "short": "MIA" },
      "New England Free Jacks": { "image": "1l5O4tYvOcIgO_NQriRNz-8OKVp4CwAgX", "short": "NEFJ" },
      "NOLA Gold": { "image": "1_Gj3WIsOmoBUbYvhmvT4AK2OKlXVoZjd", "short": "NOLA" },
      "Old Glory DC": { "image": "1ySZrTiz2x3YeijqPiHuOg_S3ZcY0IKoS", "short": "OGDC" },
      "San Diego Legion": { "image": "1e0fmlBTKyT9H4sWQ1NP9XF3LBAmzQmGC", "short": "SDL" },
      "Seattle Seawolves": { "image": "1-lwFZAHRy3BXvD6XCVlpVFEVP64UbRQ-", "short": "SEA" },
      "Utah Warriors": { "image": "1oNwMe11WywyuKuXG0BVt6DPuY72VVBOt", "short": "UTAH" },
    }
    
    # Define the form metadata
    form = {
        "info": {
            "title": f"Ranger Picks MLR Week {round}",
            "documentTitle": f"Ranger Picks MLR Week {round}",
        }
    }
    
    # Create the form
    form_response = forms_service.forms().create(body=form).execute()
    form_id = form_response.get('formId')
    print(f"Form created! View it here: https://docs.google.com/forms/d/{form_id}/edit")

    # Add questions to the form
    questions=list()
    for match in matchups:
        q={
          "title": f"{match['away']} @ {match['home']}",
          "choices": [
                {"text": f"{teams[match['away']]['short']}", "imageUrl": f"https://drive.google.com/uc?id={teams[match['away']]['image']}"},
                {"text": f"{teams[match['home']]['short']}", "imageUrl": f"https://drive.google.com/uc?id={teams[match['home']]['image']}"},
            ],
        }
        questions.append(q)

    question_body = {
        "requests": [
            {
                "createItem": {
                    "item": {
                        "title": "Ranger Name",
                        "questionItem": {
                            "question": {
                                "required": True,
                                "textQuestion": { "paragraph": False }
                            }
                        }
                    },
                    "location": {"index": 0},
                }
            }
        ]
    }
    forms_service.forms().batchUpdate(formId=form_id, body=question_body).execute()

    location_index=0
    for question in questions:
        location_index += 1
        question_body = {
            "requests": [
                {
                    "createItem": {
                        "item": {
                            "title": question["title"],
                            "questionItem": {
                                "question": {
                                    "required": True,
                                    "choiceQuestion": {
                                        "type": "RADIO",
                                        "options": [
                                            {
                                                "value": choice["text"],
                                                "image": {
                                                    "sourceUri": choice["imageUrl"],
                                                    "altText": choice["text"]
                                                },
                                            } for choice in question["choices"]
                                        ],
                                        "shuffle": False,
                                    }
                                }
                            }
                        },
                        "location": {"index": location_index},
                    }
                }
            ]
        }
        forms_service.forms().batchUpdate(formId=form_id, body=question_body).execute()
        
    batch_update_request = {
        "requests": [
            {
                "updateFormInfo": {
                    "info": {
                        "image": {
                            "sourceUri": "https://drive.google.com/uc?id=1j9Jkjdk7QB4Qm0gl_w031BT0Wd7ev22t"  # Replace with a valid, public image URL
                        }
                    },
                    "updateMask": "image"
                },
                "updateFormInfo": {
                    "info": {
                        "description": (
                            "Calling all Rangers!\n"
                            "Ball Revere and The Jacks Rangers Show are running a friendly contest for which Ranger can predict the future the best.\n\n"
                            f"Enter your picks for round {round} of MLR 2025.  Please remember your Ranger Name and keep it consistent through the year."
                        )
                    },
                    "updateMask": "description"
                },

            }
        ]
    }

    forms_service.forms().batchUpdate(
        formId=form_id, body=batch_update_request).execute()
        
    # Get the file ID (Google Drive ID) of the form
    file_id = form_id  # The Form ID is also the Drive File ID

    # Share the form with your normal account
    user_email = "john@sackheads.org"  # Replace with your email
    permission = {
        "type": "user",
        "role": "writer",  # Grant edit access
        "emailAddress": user_email
    }
    drive_service.permissions().create(
        fileId=file_id,
        body=permission,
        sendNotificationEmail=True  # Send an email notification to your account
    ).execute()
    
    print("\nNeed to edit form to require responder input email, send copy of answers, do not send link to submit again\nDon't forget to link to spreadsheet")
    
    
def get_matches(round):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
    session=requests.Session()
    html=session.get('https://www.majorleague.rugby/schedule/',headers=headers)
    soup=BeautifulSoup(html.text, features="html.parser")
    
    # check for an error
    error=soup.find_all('div','common-section')
    for err in error:
        if 'Error fetching match data' in err.text:
            raise SystemExit(err.text)

    result=list()
    allmatches=soup.find_all('div',class_='list')
    for match in allmatches:
        matchsoup=BeautifulSoup(str(match), features="html.parser")
        matchround=matchsoup.findAll('div','match-round')[0].text.split()[1]
        matchhome=matchsoup.findAll('div','team-name-result-left')[0].h3.string
        matchaway=matchsoup.findAll('div','team-name-result-right')[0].h3.string
        if matchround == f"{round}":
            result.append({ "home": matchhome, "away": matchaway})
    return(result)
    
if __name__ == "__main__":
    for round in range(1,3):
        weeklymatchups=get_matches(round)
        create_form(round,weeklymatchups)