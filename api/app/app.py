import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def ping(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "pong",
            }
        ),
    }

def main(event, context):
    try:
        body = json.loads(event['body'])
    except:
        body = None

    # ボディが空の場合は400を返す
    if body is None:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "message": "Bad Request",
                }
            ),
        }

    # ボディにtypeが含まれていて、url_verificationの場合は200を返す
    # SlackのEvent APIのURL Verificationのための処理
    if "type" in body and body["type"] == "url_verification":
        return {
            "statusCode": 200,
            "body": json.dumps(body),
        }

    # ここからメイン処理！
    logger.info(body)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "OK",
            }
        ),
    }
