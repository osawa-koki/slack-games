import boto3
from decimal import Decimal
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer

dynamodb = boto3.client('dynamodb')
table_name = 'slack-games-dynamodb-table'

serializer = TypeSerializer()
deserializer = TypeDeserializer()

def decimal_default_proc(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def make_action(channel_id, user, text, item_python_dict):

    words = item_python_dict['words']

    if len(words) == 0:
        # なんでもOK
        words.append(text)

    else:
        # しりとり
        last_word = words[-1]
        if last_word[-1] != text[0]:
            return {
                "result": -1,
                "message": f"「{last_word}」の後ろに「{text}」はつけられません。",
            }

        if text in words:
            return {
                "result": -1,
                "message": f"「{text}」は既に使われています。",
            }

        words.append(text)

    options = {
        'TableName': table_name,
        'Key': {
            'channel_id': {'S': channel_id}
        },
        'UpdateExpression': 'SET words = :words',
        'ExpressionAttributeValues': {
            ':words': {'L': [serializer.serialize(word) for word in words]}
        }
    }
    dynamodb.update_item(**options)

    return {
        "success": 0,
        "message": f"+++ -> 「{text}」 -> ???",
    }
