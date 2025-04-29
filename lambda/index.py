import json
import os
import requests

# あなたのFastAPIエンドポイントURLをここに貼り付け
FASTAPI_ENDPOINT = os.environ.get("FASTAPI_ENDPOINT", "https://your-colab-url/chat")

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        
        # ユーザー情報の取得（任意）
        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")

        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])

        # FastAPI に送るリクエストボディを作成
        payload = {
            "message": message,
            "conversationHistory": conversation_history
        }

        print("Sending request to FastAPI:", json.dumps(payload))

        # POST リクエストを送信
        response = requests.post(FASTAPI_ENDPOINT, json=payload)
        response.raise_for_status()  # エラーを自動で検知

        result = response.json()
        print("Response from FastAPI:", result)

        assistant_response = result.get("response", "No response")

        # 会話履歴に追加
        conversation_history.append({"role": "user", "content": message})
        conversation_history.append({"role": "assistant", "content": assistant_response})

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": conversation_history
            })
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(e)
            })
        }
