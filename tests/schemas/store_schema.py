ORDER_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "petId": {"type": "integer"},
        "quantity": {"type": "integer"},
        "shipDate": {"type": "string", "format": "date-time"},
        "status": {"type": "string"},
        "complete": {"type": "boolean"}
    },
    "required": ["id", "petId", "quantity", "shipDate", "status", "complete"],
    "additionalProperties": False
}