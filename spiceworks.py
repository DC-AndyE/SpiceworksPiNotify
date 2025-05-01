import os
import time
from datetime import datetime
from msgraph import GraphServiceClient
from kiota_abstractions.base_request_configuration import RequestConfiguration
from msgraph.generated.users.item.messages.messages_request_builder import MessagesRequestBuilder
from dotenv import load_dotenv
from gpiozero import OutputDevice
import requests

# Load environment variables
load_dotenv()
pushoverUser = os.getenv("PUSHOVER_USER")
pushoverToken = os.getenv("PUSHOVER_TOKEN")

# GPIO setup
RELAY_PIN = 26
relay = OutputDevice(RELAY_PIN, active_high=False)

# Trigger Pushover notification
def triggerNotification(title="New Email", message="New message received"):
    payload = {
        'token': pushoverToken,
        'user': pushoverUser,
        'message': message,
        'title': title,
        'priority': 1,
        'sound': 'pushover',
    }
    requests.post('https://api.pushover.net/1/messages.json', data=payload)

# Trigger the GPIO relay
def triggerRelay():
    relay.on()
    time.sleep(10)
    relay.off()

def save_last_message_id(message_id):
    with open("last_message_id.txt", "w") as f:
        f.write(message_id)

def load_last_message_id():
    try:
        with open("last_message_id.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


# Save and compare timestamps
def processEmailData(emails):

    if not emails:
        print("No emails to process")
        return
    
    # Filter out emails from known senders
    ignoreList = [
        "aemmerson@denstonecollege.net", 
        "mfinney@denstonecollege.net",
        "mtovey@denstonecollege.net",
        "support@denstonecollege.net"
    ]    
    emails = [email for email in emails if email.sender.email_address.address not in ignoreList]
    if emails.count == 0:
        # No emails to process
        print("No emails to process - post filter")
        return
    
    # Sort emails by received date and get the latest one
    latest_email = sorted(emails, key=lambda m: m.received_date_time, reverse=True)[0]

    # if the latest email is different from the last saved one, trigger notification and relay
    if latest_email.internet_message_id != load_last_message_id():
        print("New support email received - notifying", latest_email.subject)
        triggerNotification(title="New Ticket", message=latest_email.subject)
        triggerRelay()
        save_last_message_id(latest_email.internet_message_id)
    else:
        print("Latest email is the same as the last saved one - no action taken")

# Main function using Microsoft Graph
async def check_emails(graph_client: GraphServiceClient):
    query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
        select=["sender", "subject", "receivedDateTime", "internetMessageId"],
        top=10
    )
    request_config = RequestConfiguration(query_parameters=query_params)
    result = await graph_client.users.by_user_id("support@denstonecollege.net").messages.get(request_configuration=request_config)

    if result and result.value:
        processEmailData(result.value)

# Entry point for cron execution
if __name__ == "__main__":
    print("Script called at", datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    relay.off()
    time.sleep(1)  # optional: slight delay

    import asyncio
    from graph_client_builder import get_graph_client  # you need to implement this based on your auth flow

    asyncio.run(check_emails(get_graph_client()))
