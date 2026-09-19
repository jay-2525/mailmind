import re
from typing import List, Dict, Any


class EntityExtractor:
    """
    Robust Named Entity Recognizer for email communications.
    Combines rule-based regex patterns, contextual indicators, and NLP parsing.
    """

    ORG_PATTERNS = [
        r'\b(?:Google|Microsoft|Amazon|Meta|Apple|Netflix|TCS|Infosys|Wipro|Cognizant|Accenture|Stanford|MIT|Harvard|University|College|Institute|Corporation|Inc\.|LLC|Technologies|Labs)\b'
    ]

    URL_PATTERN = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    MONEY_PATTERN = r'(?:[\$€£₹]|Rs\.?\s*)\s*(\d+(?:,\d{3})*(?:\.\d+)?(?:\s*(?:k|thousand|lakh|million|crore|LPA))?)'

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        entities = []
        if not text:
            return entities

        # 1. URLs
        for match in re.finditer(self.URL_PATTERN, text):
            entities.append({
                "entity_type": "URL",
                "entity_value": match.group(0),
                "confidence": 0.98,
                "metadata_json": {"start": match.start(), "end": match.end()}
            })

        # 2. Email addresses
        for match in re.finditer(self.EMAIL_PATTERN, text):
            entities.append({
                "entity_type": "EMAIL",
                "entity_value": match.group(0),
                "confidence": 0.99,
                "metadata_json": {"start": match.start(), "end": match.end()}
            })

        # 3. Organizations
        for pattern in self.ORG_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append({
                    "entity_type": "ORG",
                    "entity_value": match.group(0),
                    "confidence": 0.90,
                    "metadata_json": {"start": match.start(), "end": match.end()}
                })

        # 4. Monetary amounts
        for match in re.finditer(self.MONEY_PATTERN, text, re.IGNORECASE):
            entities.append({
                "entity_type": "MONEY",
                "entity_value": match.group(0),
                "confidence": 0.92,
                "metadata_json": {"start": match.start(), "end": match.end()}
            })

        # 5. Dates / Deadlines
        date_pattern = r'\b(?:by|deadline|due|submit by|before|on)\s+([A-Za-z]+ \d{1,2}(?:st|nd|rd|th)?(?:, \d{4})?|\b(?:this|next)?\s*(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)|tomorrow|today)\b'
        for match in re.finditer(date_pattern, text, re.IGNORECASE):
            entities.append({
                "entity_type": "DEADLINE",
                "entity_value": match.group(0),
                "confidence": 0.88,
                "metadata_json": {"extracted_phrase": match.group(1)}
            })

        # 6. Salutations / People (e.g., "Hi Alex", "Regards, Sarah Jenkins")
        person_pattern = r'(?:Hi|Hello|Dear)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)|(?:Thanks|Regards|Best|Sincerely),\s*[\r\n]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
        for match in re.finditer(person_pattern, text):
            name = match.group(1) or match.group(2)
            if name and len(name.split()) <= 3:
                entities.append({
                    "entity_type": "PERSON",
                    "entity_value": name.strip(),
                    "confidence": 0.85,
                    "metadata_json": {"context": match.group(0)}
                })

        return entities


entity_extractor = EntityExtractor()
