import csv
import re
from datetime import datetime

def main():
    file = "C:\\Users\\Pjmcnally\\Documents\programming\\google_calendar\\Midwest_Ultimate_Calendar_2018.csv"
    with open(file, "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        data = [row for row in reader]

    events = []
    for item in data:
        date_list = parse_date(item[0])

        for date in date_list:
            temp = event(
                date,  # Date
                item[1],  # Tournament name
                item[2],  # Division
                item[3],  # Location
                item[4],  # Contact
                item[5],  # Contact email
                item[6],  # Website
                item[7]   # AUDL (???)
            )
            events.append(temp)
            print(temp)

def parse_date(date_str):
    """ Takes date string and returns list of dates.

        For example Jan 4-5 will return [Jan 4, Jan 5].
        Each item in the list will be a datetime object
    """
    dates = []
    date_format = "%b %d, %Y"

    if date_str == "TBD":
        return dates
    elif "-" in date_str:
        p = "(?P<mon>\w{3})\s*(?P<beg>\d{1,2})-(?P<end>\d{1,2})"
        match = re.search(p, date_str)
        month = match["mon"]
        begin = int(match["beg"])
        end = int(match["end"])
        for num in range(begin, end + 1):
            new_date_str = "{} {}, 2018".format(month, num)
            date = datetime.strptime(new_date_str, date_format)
            dates.append(date)
    else:
        date_str += ", 2018"
        date = datetime.strptime(date_str, date_format)
        dates.append(date)

    return dates

class event():
    def __init__(self, date, name, divison, location, contact, email, website, audl):
        self.date = date
        self.name = name
        self.division = divison
        self.location = location
        self.contact = contact
        self.email = email
        self.website = website
        self.AUDL = audl

    def __str__(self):
        basic_info = "\r\n{} {} at {} for {} players.".format(
            self.date.strftime("%b %d, %Y"),
            self.name,
            self.location,
            self.division,
        )

        if self.contact:
            contact_info = "\r\nContact {} at {}.".format(
                self.contact,
                self.email,
            )
        else:
            contact_info = ""

        if self.website:
            web_info = "\r\nSee {} for more info.".format(self.website)
        else:
            web_info = ""

        return "{}{}{}".format(
            basic_info,
            contact_info,
            web_info
        )

main()
