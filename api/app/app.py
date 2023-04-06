import json
import logging
import requests
import os
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SECRET = os.environ.get("SECRET")
SLACK_TOKEN = os.environ.get("SLACK_TOKEN")

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
        secret = event["queryStringParameters"]["secret"]
        if secret != SECRET:
            return {
                "statusCode": 403,
                "body": json.dumps(
                    {
                        "message": "Forbidden",
                    }
                ),
            }
        return {
            "statusCode": 200,
            "body": json.dumps(body),
        }

    # ボットがメッセージを送信した場合は何もしない
    if "bot_id" in body["event"]:
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "OK",
                }
            ),
        }

    # ここからメイン処理！
    url = "https://slack.com/api/chat.postMessage"
    form_data = {
        "token": SLACK_TOKEN,
        "channel": body["event"]["channel"],
        "text": "[SLACK GAMES] Hello World!",
    }
    requests.post(url, data=form_data)
    logger.info(json.dumps({
        "url": url,
        "form_data": form_data,
        "message": "Slackにメッセージを送信しました。",
    }))
    logger.info(json.dumps({
        "body": body,
        "message": "Slackにメッセージを受信しました。",
    }))

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "OK",
            }
        ),
    }
