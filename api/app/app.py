import json
import logging
import re
import requests
import os
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SECRET = os.environ.get("SECRET")
SLACK_TOKEN = os.environ.get("SLACK_TOKEN")

PATH_PARAMETERS = 'pathParameters'
QUERY_STRING_PARAMETERS = 'queryStringParameters'

GAMES = ["shiritori", "yamanote", "blackjack"]

DEFAULT_RETURN = json.dumps({
    "statusCode": 200,
    "body": json.dumps(
        {
            "message": "OK",
        }
    ),
})

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

    # リトライの場合は何もしない
    if "X-Slack-Retry-Num" in event["headers"]:
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "OK",
                }
            ),
        }

    # ボディにtypeが含まれていて、url_verificationの場合は200を返す
    # SlackのEvent APIのURL Verificationのための処理
    if "type" in body and body["type"] == "url_verification":
        query = event[QUERY_STRING_PARAMETERS]
        if query is None or "secret" not in query or query["secret"] != SECRET:
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

    url = "https://slack.com/api/chat.postMessage"
    form_data = {
        "token": SLACK_TOKEN,
        "channel": body["event"]["channel"],
        "text": "",
    }

    # メンション(コマンド)かどうかを判定する
    if body["event"]["type"] == "app_mention":
        # メンションされたメッセージを取得する
        message = body["event"]["text"]
        # メンションされたメッセージをスペースで分割する
        message_list = message.split(" ")
        try:
            # メンションされたメッセージの2番目の要素をコマンドとして取得する
            command = message_list[1]
            target = message_list[2]

            if command == "help":
                raise Exception("")

            if command == "create" and target not in GAMES:
                form_data["text"] = "指定したゲームが存在しません。\n"
                form_data["text"] += f"ゲーム一覧: {', '.join(GAMES)}"
                requests.post(url, data=form_data)
                return DEFAULT_RETURN

            if command == "create":
                form_data["text"] = f"{target}を作成しました。"
                requests.post(url, data=form_data)
                return DEFAULT_RETURN

            if command == "start":
                form_data["text"] = "ゲームを開始しました。"
                requests.post(url, data=form_data)
                return DEFAULT_RETURN

            if command == "stop":
                form_data["text"] = "ゲームを終了しました。"
                requests.post(url, data=form_data)
                return DEFAULT_RETURN

            if command == "status":
                form_data["text"] = "ゲームの状態を表示します。"
                requests.post(url, data=form_data)
                return DEFAULT_RETURN

            if command == "join":
                form_data["text"] = "ゲームに参加しました。"
                requests.post(url, data=form_data)
                return DEFAULT_RETURN

            if command == "leave":
                form_data["text"] = "ゲームから退出しました。"
                requests.post(url, data=form_data)
                return DEFAULT_RETURN
        except:
            # 例外が発生した場合はヘルプを表示する
            form_data["text"] = """
【コマンド一覧】
help: ヘルプを表示します。
create <game>: ゲームを作成します。
start: ゲームを開始します。
stop: ゲームを終了します。
status: ゲームの状態を表示します。
join: ゲームに参加します。
leave: ゲームから退出します。
hello: 'こんにちは'と返します。
bye: 'さようなら'と返します。
            """.strip()
            requests.post(url, data=form_data)
    else:
        # メンションされたメッセージは無視する
        # app_mentionとmessage.channelsの両方で反応してしまうため
        check_regex = r"^<@[\d\w]+>"
        if re.match(check_regex, body["event"]["text"]):
            return DEFAULT_RETURN

        logger.info(json.dumps({
            "url": url,
            "form_data": form_data,
            "message": "Slackにメッセージを送信しました。",
        }))
        logger.info(json.dumps({
            "body": body,
            "message": "Slackからメッセージを受信しました。",
        }))
        form_data["text"] = "未実装です。"
        requests.post(url, data=form_data)

    return DEFAULT_RETURN
