from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User, OAuthAccount
from app.models.action import CalendarEvent, AuditLog
from app.integrations.calendar_service import calendar_service

router = APIRouter()


@router.get("/events")
def list_calendar_events(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    events = db.query(CalendarEvent).filter(CalendarEvent.user_id == user.id).order_by(CalendarEvent.start_time.asc()).all()
    return [
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "start_time": e.start_time,
            "end_time": e.end_time,
            "location": e.location,
            "attendees": e.attendees or [],
            "status": e.status,
            "google_event_id": e.google_event_id
        }
        for e in events
    ]


@router.post("/events/{event_id}/push")
def push_event_to_calendar(
    event_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id, CalendarEvent.user_id == user.id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    oauth_acc = db.query(OAuthAccount).filter(OAuthAccount.user_id == user.id).first()
    access_token = oauth_acc.access_token if oauth_acc else "demo_token"

    res = calendar_service.create_event(
        title=event.title,
        start_time=event.start_time,
        end_time=event.end_time,
        description=event.description,
        location=event.location,
        attendees=event.attendees,
        access_token=access_token
    )

    event.status = "CONFIRMED"
    event.google_event_id = res.get("event_id")
    db.add(AuditLog(
        user_id=user.id,
        event_type="CALENDAR_EVENT_CREATED",
        target_resource=f"calendar:{event.id}",
        action_taken=f"Pushed event to Google Calendar: {event.title}",
        performed_by="USER",
        metadata_json=res
    ))
    db.commit()

    return {
        "status": "SUCCESS",
        "event_id": event.id,
        "google_event_id": event.google_event_id,
        "message": f"Calendar event '{event.title}' confirmed."
    }
