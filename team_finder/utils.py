import json

def parse_json_body(request):
    ctype = (request.content_type or "").lower()
    if "application/json" in ctype and request.body:
        try:
            return json.loads(request.body.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}
    return {}
