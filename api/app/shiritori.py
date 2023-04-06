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

def terminate_shiritori(channel_id):
    options = {
        'TableName': table_name,
        'Key': {
            'channel_id': {'S': channel_id}
        }
    }
    dynamodb.delete_item(**options)

def make_action(channel_id, user, text, item_python_dict):

    words = item_python_dict['words']

    # んで終わる単語
    if text[-1] == 'ん':
        terminate_shiritori(channel_id)
        words_str = " -> ".join(words)
        return {
            "result": 1,
            "message": f"「{text}」でしりとり終了！\n\n{words_str}",
        }

    if len(words) == 0:
        # なんでもOK
        words.append(text)
        last_word = ""

    else:
        # しりとり
        last_word = words[-1]
        if last_word[-1] != text[0]:
            terminate_shiritori(channel_id)
            words_str = " -> ".join(words)
            return {
                "result": -1,
                "message": f"「{last_word}」の後ろに「{text}」はつけられません。\n\n{words_str}",
            }

        if text in words:
            terminate_shiritori(channel_id)
            words_str = " -> ".join(words)
            return {
                "result": -1,
                "message": f"「{text}」は既に使われています。\n\n{words_str}",
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
        "result": 0,
        "message": f"{last_word} -> 「{text}」 -> ???",
    }
