import requests

def send_pushover_notification(token, user, message, title=None, priority=None):
    """
    Send a notification to Pushover.
    
    Args:
        token (str): Your Pushover application API token
        user (str): Your Pushover user key
        message (str): The message to send
        title (str, optional): The title of the notification
        priority (int, optional): Message priority (-2 to 2)
    
    Returns:
        dict: The JSON response from the Pushover API
    """
    # Create the payload
    payload = {
        'token': token,
        'user': user,
        'message': message
    }
    
    # Add optional parameters if provided
    if title:
        payload['title'] = title
    if priority is not None:
        payload['priority'] = priority
    
    # Send the request
    response = requests.post('https://api.pushover.net/1/messages.json', data=payload)
    
    # Check if the request was successful
    response.raise_for_status()
    
    # Return the response as JSON
    return response.json()

# Example usage
if __name__ == "__main__":
    # Replace these with your actual values
    APP_TOKEN = "asb5yyfznz4rfv1fw2smypun62oo27"
    USER_KEY = "XUunU9VKQxhZExmdjCkZRwrfiXFwMw"
    
    try:
        result = send_pushover_notification(
            token=APP_TOKEN,
            user=USER_KEY,
            message="Hello from Raspberry Pi!",
            title="Raspberry Pi Notification",
            priority=0
        )
        print("Notification sent successfully!")
        print(result)
    except requests.exceptions.RequestException as e:
        print(f"Error sending notification: {e}")