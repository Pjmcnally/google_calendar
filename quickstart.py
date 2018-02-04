"""
Found at: https://developers.google.com/google-apps/calendar/create-events
"""

# TODO: Continue following instructions
# TODO: Get CSV file
# TODO: Figure out how to create event
# TODO: Figure out how to access calendar

from __future__ import print_function
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

def get_events(service, calendar):
    """ List of the next 10 events on the specified calendar. """

    now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId=calendar, timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
        return False
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

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
    calendar = 'amcnallan@gmail.com'

    # Establish Credentials
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())

    # Create service object
    service = discovery.build('calendar', 'v3', http=http)

    event = {
      'summary': 'Patrick\'s Test Event',
      'location': '800 Howard St., San Francisco, CA 94103',
      'description': 'A chance to hear more about Google\'s developer products.',
      'start': {
        'date': '2018-02-06',
        'timeZone': 'America/Los_Angeles',
      },
      'end': {
        'date': '2018-02-08',
        'timeZone': 'America/Los_Angeles',
      },
      # 'recurrence': [
      #   'RRULE:FREQ=DAILY;COUNT=2'
      # ],
      # 'attendees': [
      #   {'email': 'lpage@example.com'},
      #   {'email': 'sbrin@example.com'},
      # ],
      # 'reminders': {
      #   'useDefault': False,
      #   'overrides': [
      #     {'method': 'email', 'minutes': 24 * 60},
      #     {'method': 'popup', 'minutes': 10},
      #   ],
      # },
    }

    event = service.events().insert(calendarId=calendar, body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))


if __name__ == '__main__':
    main()
