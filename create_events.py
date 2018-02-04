"""
Based on guide found at:
https://developers.google.com/google-apps/calendar/create-events

This worked, however, there are several hoops to jump around with regard to
authentication and calendar id's. A new approach is to rewrite the csv to a
google calendar supported format.

Example: https://support.google.com/calendar/answer/37118?hl=en
"""

# My imports
from datetime import datetime, date, timedelta
import csv
import re
import secret

# Imports for google code
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

def main(method):
    # Get events from Ultimate CSV
    events = get_events(secret.file)

    if method == "api":
        upload_events_api(events)
    elif method == "csv":
        create_events_csv(events)
    else:
        print("No valid method chosen")


def create_events_csv(events):
    with open('events_for_google.csv', 'w') as output:
        fieldnames = ['Subject', 'Start Date', 'Start Time', 'End Date',
            'End Time', 'All Day Event', 'Description', 'Location', 'Private']
        writer = csv.DictWrite(output, fieldnames=fieldnames)

        writer.writeheader()
        for event in events:
            pass


def upload_events_api(events):
    # Define calendar
    calendar = secret.calendar

    # Establish Credentials
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())

    # Create Google service object
    service = discovery.build('calendar', 'v3', http=http)

    for event in events:
        event_body = event.get_google_event()
        # event = service.events().insert(calendarId=calendar, body=event_body).execute()
        # print('Event created: %s' % (event.get('htmlLink')))
        print(event_body)


def get_events(csv_file):
    with open(csv_file, "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        data = [row for row in reader]

    events = []
    for row in data:
        event_obj = event(*row)
        events.append(event_obj)

    return events


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


class event():
    def __init__(self, date_str, name, division, location, contact, email, website, audl):
        self.date_str = date_str
        self.date_list = self.parse_date_str(date_str)
        self.name = name
        self.division = "Multi-Division" if division == "All" else division
        self.location = location
        self.contact = contact
        self.email = email
        self.website = website
        self.AUDL = audl

    def __str__(self):
        out_str = "\r\nDate: {date}\r\nName: {name}\r\nLocation: {loc}".format(
            date=self.date_str,
            name=self.name,
            loc=self.location
        )

        if self.division:
            out_str += "\r\nDivision: {}".format(self.division)
        if self.contact:
            out_str += "\r\nContact: {}".format(self.contact)
        if self.email:
            out_str += " at {}".format(self.email)
        if self.website:
            out_str += "\r\nWebsite: {}".format(self.website)

        return out_str

    def get_start_date(self):
        return self.date_list[0]

    def get_end_date(self):
        return self.date_list[-1]

    def parse_date_str(self, date_str):
        """ Takes date string and returns list of dates.

            For example Jan 4-5 will return [Jan 4, Jan 5].
            Each item in the list will be a datetime object
        """
        dates = []
        year = "2018"  # Hard coded magic number. dang...
        date_format = "%b %d, %Y"

        if date_str == "TBD":
            return [""]
        elif "-" in date_str:  # If a date range is indicated:
            p = "(?P<m1>\w{3})\s*(?P<d1>\d{1,2})-(?P<m2>\w{3})*(?P<d2>\s*\d{1,2})"
            match = re.search(p, date_str)

            beg_mon = match["m1"]
            beg_day = match["d1"]
            beg_date_str = "{} {}, {}".format(beg_mon, beg_day, year)
            beg_date = datetime.strptime(beg_date_str, date_format).date()

            end_mon = match["m2"] if match["m2"] else match["m1"]
            end_day = match["d2"]
            end_date_str = "{} {}, {}".format(end_mon, end_day, year)
            end_date = datetime.strptime(end_date_str, date_format).date()

            days = (end_date - beg_date).days
            for day in range(0, days + 2):  # + 2 because google's all day events are non inclusive
                cur_date = beg_date + timedelta(day)
                dates.append(cur_date)
        else:  # If only one date is indicated:
            date_str = "{}, {}".format(date_str, year)
            date = datetime.strptime(date_str, date_format).date()
            dates.append(date)

        return dates

    def get_formatted_description(self):
        description = "{} Ultimate Event in {}".format(self.division, self.location)
        if self.contact:
            description += "\r\nContact Name: {}".format(self.contact)
        if self.email:
            description += "\r\nContact Email: {}".format(self.email)
        if self.website:
            description += "\r\nWebsite: {}".format(self.website)
        return description

    def get_formatted_title(self):
        return "{} - {} Ultimate Event".format(self.name, self.division),

    def get_google_event(self):
        event = {
            'summary': self.get_formatted_title()
            'location': self.location,
            'description': self.get_formatted_description(),
            'start': {
            'date': self.date_list[0].strftime("%Y-%m-%d"),
            },
            'end': {
            'date': self.date_list[-1].strftime("%Y-%m-%d"),
            },
        }

        return event

    def print_dates(self):
        for date in self.date_list:
            print(date.strftime("%b %d, %Y"))

main("api")
