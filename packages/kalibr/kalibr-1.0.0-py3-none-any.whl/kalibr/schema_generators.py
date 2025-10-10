import json

def generate_openapi_schema(app):
    return app.openapi()

def generate_mcp_schema(app):
    return {
        "mcp": "1.0",
        "tools": [
            {"name": name, "description": func.__doc__ or ""}
            for name, func in app.actions.items()
        ],
    }
