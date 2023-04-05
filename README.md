# slack-games

🍺🍺🍺 Slack上で遊べるゲームを作ってみた！  

## 準備

以下のGitHub Secretsを設定します。  

| Name | Value |
| --- | --- |
| AWS_ACCESS_KEY_ID | AWSアクセスキー |
| AWS_SECRET_ACCESS_KEY | AWSシークレットキー |
| AWS_REGION | AWSリージョン |

## 開発用実行

```shell
cd ./api
sam build --use-container ;; sam local start-api
```
