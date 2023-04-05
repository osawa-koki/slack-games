import json

def ping(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "pong",
            }
        ),
    }

def url_verify(event, context):
    body = event["body"]
    return {
        "statusCode": 200,
        "body": json.dumps(body),
    }
