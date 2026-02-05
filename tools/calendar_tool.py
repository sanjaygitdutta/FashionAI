import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

#read-only calender access
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_events() -> dict:
    """
    Fetch the next 5 upcoming events from the user's Google Calendar.
    Used by gemini to understand the user's sechedule context.
    """
    creds = None

    # load exiting token if available
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # refresh or request new credentials if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

    # save the credentials for future use
    with open("token.json", "w") as token:
        token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        now = datetime.datetime.utcnow().isoformat() + "Z"

        events_result = service.events().list(
            calendarId="primary",
            timeMin=now,
            maxResults=5,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        
        events = events_result.get("items", [])
        
        if not events:
            return{
                "success": True,
                "events": [],
                "message": "No upcoming events found."
            }
        
        formatted_events = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            formatted_events.append({
                "summary": event.get("summary", "No Title"),
                "start": start,
                "location": event.get("location", "Not specified")
            })

        return{
            "success": True,
            "events": formatted_events
        }
    except Exception as e:
        return{
            "success": False,
            "error": f"Calendar API error: {str(e)}"
        }
   
#independent testing
if __name__ == "__main__":
    print("Fetching upcoming calendar events...")
    print(get_calendar_events())