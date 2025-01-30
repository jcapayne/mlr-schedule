#!/usr/bin/env python3


# make sure we're running under the virtual environment
import os

my_path = os.path.abspath(os.path.dirname(__file__))

activate_this_file = "%s/bin/activate_this.py" % my_path

exec(open(activate_this_file).read(), {'__file__': activate_this_file})


from google.oauth2 import service_account
from googleapiclient.discovery import build
import sys

# Path to your service account key JSON file
SERVICE_ACCOUNT_FILE = "%s/ranger-picks-d38ed51e8adc.json" % my_path

# Google Drive API scope
SCOPES = ['https://www.googleapis.com/auth/drive']

def delete_google_form(file_id):
    # Authenticate using the service account
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    # Build the Drive API client
    drive_service = build('drive', 'v3', credentials=credentials)
    
    try:
        # Delete the file (Google Form)
        drive_service.files().delete(fileId=file_id).execute()
        print(f"Form with file ID {file_id} has been deleted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Replace with the file ID of the form you want to delete
    if len(sys.argv) > 1:
        for form_file_id in sys.argv[1:]:
            #form_file_id = sys.argv[1]
            delete_google_form(form_file_id)
    else:
        print("need a form ID\n")