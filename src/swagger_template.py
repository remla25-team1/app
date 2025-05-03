def generate_swagger_doc(summary = "", description ="", request_example=None, response_example=None, required_fields=None):
    request_example = request_example or {}
    response_example = response_example or {}
    required_fields = required_fields or []
    return {
        "summary": summary,
        "description": description,
        "consumes": ["application/json"],
        "parameters": [
            {
                "name": "input",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "required": required_fields,
                    "properties": {
                        key: {
                            "type": "string",
                            "example": value
                        } for key, value in request_example.items()
                    }
                }
            }
        ],
        "responses": {
            200: {
                "description": "Successful response",
                "schema": {
                    "type": "object",
                    "properties": {
                        key: {
                            "type": "string" if isinstance(value, str) else "integer",
                            "example": value
                        } for key, value in response_example.items()
                    }
                }
            }
        }
    }
