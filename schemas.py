USER_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {
            "type": "integer"
        },
        "name": {
            "type": "string"
        },
        "username": {
            "type": "string"
        },
        "email": {
            "type": "string"
        },
        "address": {
            "type": "object",
            "properties": {
                "street": {
                    "type": "string"
                },
                "suite": {
                    "type": "string"
                },
                "city": {
                    "type": "string"
                },
                "zipcode": {
                    "type": "string"
                },
                "geo": {
                    "type": "object",
                    "properties": {
                        "lat": {
                            "type": "string"
                        },
                        "lng": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "lat",
                        "lng"
                    ]
                }
            },
            "required": [
                "street",
                "suite",
                "city",
                "zipcode",
                "geo"
            ]
        },
        "phone": {
            "type": "string"
        },
        "website": {
            "type": "string"
        },
        "company": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string"
                },
                "catchPhrase": {
                    "type": "string"
                },
                "bs": {
                    "type": "string"
                }
            },
            "required": [
                "name",
                "catchPhrase",
                "bs"
            ]
        }
    },
    "required": [
        "id",
        "name",
        "username",
        "email",
        "address",
        "phone",
        "website",
        "company"
    ]
}

USERS = {
    "type": "array",
    "items": USER_SCHEMA
}

TASKS_SCHEMA = {
    "type": "object",
    "properties": {
        "userId": {
            "type": "integer"
        },
        "id": {
            "type": "integer"
        },
        "title": {
            "type": "string"
        },
        "completed": {
            "type": "boolean"
        }
    },
    "required": [
        "userId",
        "id",
        "title",
        "completed"
    ]
}

TASKS = {
    "type": "array",
    "item": TASKS_SCHEMA
}
