from flask import Flask, request, abort, jsonify
import base64
import requests

# from dotenv import load_dotenv
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    ImageMessage,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
import os
# load_dotenv()

configuration = Configuration(access_token=os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return '<h1> python寫的 LINEBOT大叫: About!</h1>'

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

## 20250121
# To handle the picture from message ID:
def get_message_pic(message_id, ACCESS_TOKEN):
    url=f'https://api-data.line.me/v2/bot/message/{message_id}/content'
    headers={"Authorization":f"Bearer {ACCESS_TOKEN}"}
    response=requests.get(url,headers=headers, stream=True)
    response.raise_for_status()
    return response

# To handle the picutre AI recognition: (local端 LMStudio, devtunnel service port 3030)
def send_image_to_AI(image_path):
    with open(image_path, 'rb') as f:
        encoded_string=base64.b64encode(f.read()).decode('utf-8')
    data={
        "model": "llava-v1.5-7b",
        "messages": [
            { 
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": "What is this image?"
                },
                {
                "type": "image_url",
                "image_url": { "url": f"data:image/png;base64,{encoded_string}" }
                }
            ]
            }
        ],
        "temperature": 0.7,
        "max_tokens": -1,
        "stream": False
    }
    headers={"Content-Type": "application/json"}
    response=requests.post("https://c8jkzw1b-3030.asse.devtunnels.ms/v1/chat/completions", headers=headers, json=data)
    response.raise_for_status()
    print(response.json())
    result=response.json()['choices'][0]['message']['content']
    # return response
    return result

## 往後延伸 text chat
# def chat_completions(input_text):
#     data={}


# @line_handler.add(MessageEvent, message=TextMessageContent)
@line_handler.add(MessageEvent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        # print(event)
        if event.message.type == 'text':
            print(f"Hello~ message {event.message.id} type=text")
        elif event.message.type == 'image':
            message_pic=get_message_pic(event.message.id, os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
            image_path=os.path.join('pic','downloadimg.jpg')
            with open(image_path, 'wb') as f:
                for i in message_pic.iter_content():
                    f.write(i)

            print(f"picture saved")

            img_result=send_image_to_AI(image_path) ## 傳給 AI LMStudio
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                # messages=[TextMessage(text=event.message.text)]
                messages=[TextMessage(text=img_result)]
            )
        )
        print(f"{event.timestamp} msg from {event.source} : {event.message.text}")

if __name__ == '__main__':
    app.run(debug=True)