"""Mock data for testing."""

MOCK_INDICATOR_RESPONSE = {
    "id": 12345,
    "type": "Address",
    "summary": "192.168.1.1",
    "rating": 3.5,
    "confidence": 85,
    "dateAdded": "2024-01-15T14:32:10Z",
    "lastModified": "2025-11-22T09:15:43Z",
    "ownerName": "MyOrganization",
    "ownerId": 1,
    "webLink": "https://example.threatconnect.com/auth/indicators/details/address.xhtml?address=192.168.1.1",
    "description": "Known C2 server for malware family XYZ",
    "active": True,
    "tags": [
        {"name": "malware"},
        {"name": "c2"},
        {"name": "apt29"}
    ],
    "attributes": [
        {
            "id": 1,
            "type": "Source",
            "value": "OSINT Report #1234",
            "dateAdded": "2024-01-15T14:32:10Z",
            "lastModified": "2024-01-15T14:32:10Z"
        }
    ]
}

MOCK_GROUP_RESPONSE = {
    "id": 67890,
    "type": "Incident",
    "name": "Network Intrusion January 2024",
    "dateAdded": "2024-01-20T10:00:00Z",
    "lastModified": "2024-01-25T15:30:00Z",
    "ownerName": "MyOrganization",
    "ownerId": 1,
    "webLink": "https://example.threatconnect.com/auth/incident/incident.xhtml?incident=67890",
    "description": "Detected network intrusion via C2 communication",
    "eventDate": "2024-01-18T00:00:00Z",
    "status": "Open"
}

MOCK_SEARCH_RESULT = {
    "data": [MOCK_INDICATOR_RESPONSE],
    "count": 1
}
