"""
Found at: https://developers.google.com/google-apps/calendar/create-events
"""

import secret
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from datetime import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_events(service, calendar, num):
    """ List of the next 10 events on the specified calendar. """

    now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming {} events'.format(num))
    eventsResult = service.events().list(
        calendarId=calendar, timeMin=now, maxResults=num, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
        return False
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        print("{} to {}: {}".format(start, end, event['summary']))

    return True

def quick_add_event(service, calender, text):
    created_event = service.events().quickAdd(
        calendarId=calendar,
        text=text
    ).execute()

    return created_event['id']

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object.
    """

    # Define calendar
    calendar = secret.calendar

    # Establish Credentials
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())

    # Create service object
    service = discovery.build('calendar', 'v3', http=http)

    events = get_events(service, calendar, 88)

if __name__ == '__main__':
    main()
