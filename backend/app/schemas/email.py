from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class ExtractedEntityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    entity_type: str
    entity_value: str
    confidence: float
    metadata_json: Dict[str, Any] = {}


class EmailAnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    category: str
    importance: float
    urgency: float
    actionability: float
    storage_waste_score: float
    is_promotional: bool
    is_job_related: bool
    security_risk_level: str
    security_risk_reasons: List[str] = []
    summary: Optional[str] = None
    raw_analysis: Dict[str, Any] = {}
    analyzed_at: datetime


class EmailRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    thread_id: str
    message_id_external: str
    sender: str
    sender_name: Optional[str] = None
    recipients: List[str] = []
    subject: str
    body_text: str
    body_html: Optional[str] = None
    received_at: datetime
    labels: List[str] = []
    size_bytes: int
    has_attachments: bool
    attachment_metadata: List[Dict[str, Any]] = []
    processing_status: str
    analysis: Optional[EmailAnalysisRead] = None
    entities: List[ExtractedEntityRead] = []


class EmailThreadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    thread_id_external: str
    subject: Optional[str] = None
    snippet: Optional[str] = None
    message_count: int
    last_message_at: datetime
    emails: List[EmailRead] = []
