"""
Based on guide found at:
https://developers.google.com/google-apps/calendar/create-events

This worked, however, there are several hoops to jump around with regard to
authentication and calendar id's. A new approach is to rewrite the csv to a
google calendar supported format.

Example: https://support.google.com/calendar/answer/37118?hl=en
"""

# My imports
from argparse import ArgumentParser
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


def main(method, test):
    # Get events from Ultimate CSV
    events = get_events(secret.file)

    if method == "api":
        upload_events_api(events, test)
    elif method == "csv":
        create_events_csv(events, test)
    elif method == "print":
        for event in events:
            print(event)


def parse_args():
    parser = ArgumentParser(description="Create Events from CSV formatted for Google Calendar")

    # Add required argument "method"
    parser.add_argument(
        "method",
        help="The method by which to create the events",
        choices=['api', 'csv', "print"],
        type=str,
    )

    # Add optional argument "Test mode"
    parser.add_argument(
        "-t",
        "--test",
        help="Run in test mode",
        action='store_true',
    )

    # Parse argument and run test with provided arguements
    return parser.parse_args()


def create_events_csv(events, test):
    with open('events_for_google.csv', 'w', newline='') as output:
        fieldnames = ['Subject', 'Start Date', 'Start Time', 'End Date',
            'End Time', 'All Day Event', 'Description', 'Location', 'Private']
        writer = csv.DictWriter(output, fieldnames=fieldnames)

        writer.writeheader()
        for event in events:
            row = {
                'Subject': event.get_formatted_title(),
                'Start Date': event.start_date.strftime("%Y-%m-%d"),
                # timedelta + 1 because Google processes end dates as exclusive
                'End Date': (event.end_date + timedelta(1)).strftime("%Y-%m-%d"),
                'All Day Event': True,
                'Description': event.get_formatted_description(),
                'Location': event.location,
            }

            if test:
                print(row)
            else:
                writer.writerow(row)


def upload_events_api(events, test):
    # If modifying these scopes, delete your previously saved credentials
    # at ~/.credentials/calendar-python-quickstart.json
    scopes = secret.scopes
    client_secret_file = secret.client_secret_file
    app_name = secret.app_name

    # Establish Credentials
    credentials = get_credentials(scopes, client_secret_file, app_name)
    http = credentials.authorize(httplib2.Http())

    # Create Google service object
    service = discovery.build('calendar', 'v3', http=http)

    for event in events:
        event_body = format_google_event(event)

        if test:
            print(event_body)
        else:
            event = service.events().insert(
                calendarId=secret.calendar,
                body=event_body).execute()
            print('Event created: %s' % (event.get('htmlLink')))


def format_google_event(event):
    g_event = {
        'summary': event.get_formatted_title(),
        'location': event.location,
        'description': event.get_formatted_description(),
        'start': {
        'date': event.start_date.strftime("%Y-%m-%d"),
        },
        'end': {
        # timedelta + 1 because Google processes end dates as exclusive
        'date': (event.end_date + timedelta(1)).strftime("%Y-%m-%d"),
        },
    }

    return g_event


def get_credentials(scope, secret_file, app_name):
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
        flow = client.flow_from_clientsecrets(secret_file, scope)
        flow.user_agent = app_name
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_events(csv_file):
    with open(csv_file, "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        data = [row for row in reader]

    events = []
    for row in data:
        event_obj = UltimateEvent(*row)
        events.append(event_obj)

    return events


class UltimateEvent():
    def __init__(self, date_str, name, division, location, contact, email, website, audl):
        self.parse_date_str(date_str)  # sets self.start_date and self.end_date
        self.name = name
        self.division = "Multi-Division" if division == "All" else division
        self.location = location
        self.contact = contact
        self.email = email
        self.website = website
        self.AUDL = audl

    def __str__(self):
        out_str = "\r\n{date}\r\n{title}\r\n{description}".format(
            date=self.get_formatted_date(),
            title=self.get_formatted_title(),
            description=self.get_formatted_description(),
        )
        return out_str


    def parse_date_str(self, date_str):
        """ Takes date string (format 'Jan 1' or 'Apr 31-May 3') and sets
            parses it.

            This function sets self.start_date and self.end_date for this
            object.
        """

        p = "(?P<m1>\w{3})\s*(?P<d1>\d{1,2})-*(?P<m2>\w{3})*(?P<d2>\s*\d{1,2})*"
        match = re.match(p, date_str)

        year = "2018"  # Hard coded magic number. dang...
        in_date_format = "%b %d, %Y"  # example "Jan 1, 2018"

        start = "{} {}, {}".format(match["m1"], match["d1"], year)
        end = "{} {}, {}".format(
            match["m2"] if match["m2"] else match["m1"],
            match["d2"] if match["d2"] else match["d1"],
            year)

        self.start_date = datetime.strptime(start,in_date_format)
        self.end_date = datetime.strptime(end, in_date_format)


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
        return "{} - {} Ultimate Event".format(self.name, self.division)

    def get_formatted_date(self):
        if self.start_date == self.end_date:
            return self.start_date.strftime("%Y-%m-%d")
        else:
            return "{} to {}".format(
                self.start_date.strftime("%Y-%m-%d"),
                self.end_date.strftime("%Y-%m-%d"))


args = parse_args()
main(args.method, args.test)
