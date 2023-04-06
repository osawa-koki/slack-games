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

def create_game(channel_id, game_name, user):

    options = {
        'TableName': table_name,
        'Key': {
            'channel_id': {'S': channel_id}
        }
    }
    ret = dynamodb.get_item(**options)

    if 'Item' in ret:
        return {
            "success": False,
            "message": f"既にゲームが存在しています。\nterminateコマンドでゲームを終了してください。",
        }

    options = {
        'TableName': table_name,
        'Item': {
            'channel_id': {'S': channel_id},
            'game_name': {'S': game_name},
            'users': {'L': [{'S': user}]},
        }
    }
    dynamodb.put_item(**options)

    return {
        "success": True,
        "message": f"{game_name}を作成しました。",
    }

def terminate_game(channel_id):
    options = {
        'TableName': table_name,
        'Key': {
            'channel_id': {'S': channel_id}
        }
    }
    ret = dynamodb.get_item(**options)

    if 'Item' not in ret:
        return {
            "success": False,
            "message": f"ゲームが開始されていません。",
        }

    dynamodb.delete_item(**options)

    return {
        "success": True,
        "message": f"ゲームを終了しました。",
    }

def get_game_status(channel_id):
    options = {
        'TableName': table_name,
        'Key': {
            'channel_id': {'S': channel_id}
        }
    }
    ret = dynamodb.get_item(**options)

    if 'Item' not in ret:
        return {
            "success": False,
            "message": f"ゲームが開始されていません。",
        }

    # DynamoDBのレスポンスをPythonのデータ型に変換する
    item_python_dict = {
        k: deserializer.deserialize(v)
        for k, v in ret['Item'].items()
    }

    game_name = item_python_dict['game_name']
    users = item_python_dict['users']

    return {
        "success": True,
        "message": f"ゲーム: {game_name}\n参加者: {', '.join(lambda u: f'<@{u}>', users)}",
    }
