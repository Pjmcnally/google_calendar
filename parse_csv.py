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
    for row in data:
        event_obj = event(*row)
        events.append(event_obj)
        print(event_obj)
        event_obj.print_dates()



class event():
    def __init__(self, date_str, name, divison, location, contact, email, website, audl):
        self.date_str = date_str
        self.date_list = self.parse_date_str(date_str)
        self.name = name
        self.division = divison
        self.location = location
        self.contact = contact
        self.email = email
        self.website = website
        self.AUDL = audl

    def __str__(self):
        basic_info = "\r\n{} {} at {} for {} players.".format(
            self.date_str,
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

    def parse_date_str(self, date_str):
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

    def print_dates(self):
        for date in self.date_list:
            print(date.strftime("%b %d, %Y"))


main()
