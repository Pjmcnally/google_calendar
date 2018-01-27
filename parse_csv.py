import csv
from datetime import datetime

def main():
    file = "C:\\Users\\Pjmcnally\\Documents\programming\\google_calendar\\Midwest_Ultimate_Calendar_2018.csv"
    with open(file, "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        data = [row for row in reader]

    events = []
    for item in data:
        temp = event(
            item[0],  # Date
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
            self.date,
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
