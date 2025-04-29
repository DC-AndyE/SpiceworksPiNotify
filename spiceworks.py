
import requests
import re
import time
from datetime import datetime
import random
import os
import cloudscraper
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Access the values
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

from gpiozero import OutputDevice
RELAY_PIN = 26
relay = OutputDevice(RELAY_PIN, active_high=False)

# Loosely based to a script a php script for accessing an earlier version of spiceworks.
# see https://github.com/anthonyeden/spiceworks_api/blob/master/Spiceworks-External-JSON-API-v1.php

class SpiceworksSession:
    sesh = None
    email = ""
    password = ""
    testURL = "https://denstonecollegeit.on.spiceworks.com"
    loginURL = "https://accounts.spiceworks.com/sign_in"
    ticketsURL = "https://denstonecollegeit.on.spiceworks.com/api/tickets.json"
    ticketsURL = "https://on.spiceworks.com/api/main/tickets?sort=created_at-desc&page[number]=1&page[size]=10&filter[status][eq]=open"
    userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def getToken(self, respsonseText):
        # find authenticity token. If we find it we are not logged in.
        #m = re.search('name="authenticity_token".*value="(.*?)"', respsonseText)
        # Changed location of token sometime in late 2023
        m = re.search('content="authenticity_token" \/>\\n<meta name="csrf-token" content="(.*?)"', respsonseText)
        if bool(m):
            return m.group(1)
        else:   
            return None

    def login(self):

        # Check we aren't already logged in by called spiceworks and seeing if a login page is returned.

        if isinstance(self.sesh, requests.Session) == False:
            # Setup a session to automatically handle the cookies.
            self.sesh = cloudscraper.create_scraper()

        customHeaders = {"host":"accounts.spiceworks.com","User-Agent":self.userAgent}
        r = self.sesh.get(self.testURL, allow_redirects=True, headers=customHeaders)        
        authenticityToken = self.getToken(r.text)

        # If we find the login page then we must log in.
        if authenticityToken != None:
            print("Token=" + authenticityToken)
            postFields = {
                "utf8": "✓",
                "authenticity_token": authenticityToken,
                "email": self.email,
                "password": self.password,
                "success": "https://denstonecollegeit.on.spiceworks.com/auth/spiceworks/callback",
                "permission_denied:": "https://accounts.spiceworks.com/",
                "policy": "hosted_help_desk",
                "commit": "Log in"
            }

            # call the login page with the required post data
            customHeaders = {
                "Host": "accounts.spiceworks.com",
                "User-Agent": self.userAgent,
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://denstonecollegeit.on.spiceworks.com/tickets/open/1?sort=updated_at-desc",
                "Origin": "https://accounts.spiceworks.com",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9"
            }
            loginResponse = self.sesh.post(self.loginURL, data=postFields, headers=customHeaders)
            print("Login attempt response: ", loginResponse.status_code)
            return True
        else: 
            print("Already Logged in")
            return True


    def getTickets(self):
        customHeaders = {"User-Agent":self.userAgent}
        ticketResponse = self.sesh.get(self.ticketsURL,headers=customHeaders)
        print("Ticket request response: ", ticketResponse.status_code)
        if ticketResponse.status_code == 200:
            return ticketResponse.json()
        else:
            return None


def triggerNotification(title="New Ticket", message="New Ticket Alert"):
    
    pushoverUser = os.getenv("PUSHOVER_USER")
    pushoverToken = os.getenv("PUSHOVER_TOKEN")

    payload = {
        'token': pushoverToken,
        'user': pushoverUser,
        'message': message,
        'title': title,
        'priority': 1,
        'sound': 'pushover',
    }
    
    # Send the request
    response = requests.post('https://api.pushover.net/1/messages.json', data=payload)

def triggerRelay():
    relay.on()
    time.sleep(10)
    relay.off()


def processTicketData(ticketData):
    # Make sure that the previous timestamp file exists
    with open('saved_timestamp.txt', 'a'):
        pass
    
    # Do we have tickets to process?
    if ticketData and len(ticketData["tickets"]) > 0  :
        print("Ticket data retreived")

        # Check what the time of the last ticket was
        with open('saved_timestamp.txt') as text_file:
            saved_string = text_file.read()
            if(len(saved_string) == 0):
                # we don't have a previous timestamp so lets save the current timestamp and notify
                triggerNotification()
                triggerRelay()
                with open('saved_timestamp.txt', 'w') as text_file:
                    # Save the new current date
                    text_file.write(datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
            else:
                saved_date = datetime.strptime(saved_string.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                # filter out any tickets from email addresses we don't want to notify about
                ignoreEmails = ["aemmerson@denstonecollege.net",
                              "mtovey@denstonecollege.net",
                              "mfinney@denstonecollege.net",
                              "noreply@roombookingsystem.co.uk"
                              ]
                externalTickets = [ticket for ticket in ticketData["tickets"] if ticket["creator"]["email"] not in ignoreEmails]
                if(len(externalTickets)>0):
                    # Find when the latest ticket was created
                    latest_string = externalTickets[0]["created_at"]
                    latest_date = datetime.strptime(latest_string.split('.')[0],'%Y-%m-%dT%H:%M:%S')

                    with open('saved_timestamp.txt', 'w') as text_file:
                            # Save the new current date
                            text_file.write(latest_string)       
                    # If the latest ticket is newer than the last time we checked then notify
                    if latest_date > saved_date:
                        print("Recent tickets found - notifications sent")
                        title = "New Ticket from {}".format(externalTickets[0]["creator"]["name"])
                        message = externalTickets[0]["summary"]
                        triggerNotification(title, message)
                        triggerRelay()

print("Script called at ", datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))

# Reset relay
relay.off()

# Wait a variable number of seconds to try to avoid cloudflare issues
time.sleep(random.uniform(0, 10))
sw = SpiceworksSession(email, password)

sw.login()
ticketsData = sw.getTickets()
#print(ticketsData)
processTicketData(ticketsData)





