import boto3
from decimal import Decimal
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer

dynamodb = boto3.client('dynamodb')
table_name = 'slack-games-dynamodb-table'

serializer = TypeSerializer()
deserializer = TypeDeserializer()

yamanote_stations = [
  "おおさき",
  "しながわ",
  "たまち",
  "はままつちょう",
  "しんばし",
  "ゆうらくちょう",
  "とうきょう",
  "かんだ",
  "あきはばら",
  "おかちまち",
  "うえの",
  "うぐいすだに",
  "にっぽり",
  "にしにっぽり",
  "たばた",
  "こまごめ",
  "すがも",
  "おおつか",
  "いけぶくろ",
  "めじろ",
  "たかだのばば",
  "しんおおくぼ",
  "しんじゅく",
  "よよぎ",
  "はらじゅく",
  "しぶや",
  "えびす",
  "めぐろ",
  "ごたんだ"
]

def decimal_default_proc(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def terminate_yamanote(channel_id):
    options = {
        'TableName': table_name,
        'Key': {
            'channel_id': {'S': channel_id}
        }
    }
    dynamodb.delete_item(**options)

def make_action(channel_id, user, text, item_python_dict):

    stations = item_python_dict['stations']

    # 存在しない場合
    if text not in yamanote_stations:
        terminate_yamanote(channel_id)
        stations_str = " -> ".join(stations)
        return {
            "result": -1,
            "message": f"「{text}」は山手線に存在しません。\n\n{stations_str}",
        }

    # すでに使われている場合
    if text in stations:
        terminate_yamanote(channel_id)
        stations_str = " -> ".join(stations)
        return {
            "result": -1,
            "message": f"「{text}」は既に使われています。\n\n{stations_str}",
        }

    stations.append(text)

    options = {
        'TableName': table_name,
        'Key': {
            'channel_id': {'S': channel_id}
        },
        'UpdateExpression': 'SET stations = :stations',
        'ExpressionAttributeValues': {
            ':stations': {'L': [serializer.serialize(word) for word in stations]}
        }
    }
    dynamodb.update_item(**options)

    return {
        "result": 0,
        "message": f"🚉🚉🚉🚉🚉",
    }
