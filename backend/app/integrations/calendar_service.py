from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


class CalendarService:
    """
    Google Calendar API integration service for creating events after explicit human approval.
    """

    def create_event(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        access_token: Optional[str] = None
    ) -> Dict[str, Any]:
        if not access_token or access_token.startswith("demo_"):
            return {
                "status": "SUCCESS",
                "event_id": f"cal_evt_demo_{int(datetime.now().timestamp())}",
                "html_link": "https://calendar.google.com/calendar/r/eventedit",
                "simulated": True
            }

        try:
            creds = Credentials(token=access_token, token_uri="https://oauth2.googleapis.com/token")
            service = build("calendar", "v3", credentials=creds)

            event_body = {
                "summary": title,
                "description": description or "",
                "location": location or "",
                "start": {"dateTime": start_time.isoformat(), "timeZone": "UTC"},
                "end": {"dateTime": end_time.isoformat(), "timeZone": "UTC"},
            }
            if attendees:
                event_body["attendees"] = [{"email": a} for a in attendees]

            event = service.events().insert(calendarId="primary", body=event_body).execute()
            return {
                "status": "SUCCESS",
                "event_id": event.get("id"),
                "html_link": event.get("htmlLink"),
                "simulated": False
            }
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}


calendar_service = CalendarService()
