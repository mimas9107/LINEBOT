from flask import Flask, request, abort, jsonify
import base64
import requests
import time

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

# 2025/02/06 要串接 google gemini, 
import google.generativeai as textgenai
# 取 gemini api key.
textgenai.configure(api_key=os.environ["GEMINI_API_KEY"])
# 要串接 gemini傳圖功能: https://ai.google.dev/gemini-api/docs/vision?hl=zh-tw&lang=python

## pic to gemini
from google import genai
import PIL.Image
import json #20250328

CHAT_HISTORY_LENGTH=5 ## 2020330定義要擷取幾則歷史訊息.

configuration = Configuration(access_token=os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

GOOGLE_APPS_SCRIPT_URL=os.getenv("GOOGLE_APPS_SCRIPT_URL") #20250328

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

# 2025/02/06 串接 gemini.
def GeminiChatBot(prompt_input):
    # Create the model
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = textgenai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=generation_config,
    )

    chat_session = model.start_chat(
        history=[
        ]
    )

    response = chat_session.send_message(prompt_input)
    return response.text

# pic to Gemini
def GeminiChatBot_pic():
    # 改本地端載入影像:
    image_path="pic/downloadimg.jpg"
    image=PIL.Image.open(image_path)

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        # 原始範例:
        # contents=["What is this image?",
        #           types.Part.from_bytes(image.content, "image/jpeg")])
        contents=["這張圖是什麼?",
                image])
    # print(response.text)
    return "你上傳了一張圖,\n ai回答: \n "+response.text

def get_chat_history(user_id):
    if not GOOGLE_APPS_SCRIPT_URL:
        print("GOOGLE_APPS_SCRIPT_URL environment variable not set.")
        return []

    # history_url = f"{GOOGLE_APPS_SCRIPT_URL}?action=get_history&userId={user_id}&limit={CHAT_HISTORY_LENGTH}"
    history_url=GOOGLE_APPS_SCRIPT_URL
    payload={
        "action":"get_history",
        "userId":user_id,
        "limit":CHAT_HISTORY_LENGTH
    }
    headers={'Content-Type':'application/json'}
    try:
        # response = requests.get(history_url)
        response=requests.post(history_url, headers=headers, data=json.dumps(payload))
        print(f"[get_chat_history] response={response.content}")

        response.raise_for_status()
        history_data = response.json().get("history", [])
        print(f"[get_chat_history] history_data={history_data}")

        return history_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching chat history: {e}")
        return []


# @line_handler.add(MessageEvent, message=TextMessageContent)
@line_handler.add(MessageEvent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        # print(event)

        #20250328
        user_message_text="" 
        user_message_type=event.message.type
        timestamp=event.timestamp
        user_id = event.source.user_id if event.source.type == "user" else (event.source.group_id if event.source.type == "group" else event.source.room_id if event.source.type == "room" else "unknown")

        if event.message.type == 'text':
            print(f"Hello~ message {event.message.id} type=text")
            user_message_text=event.message.text

            # 2025/02/06 塞咒語訊息到 gemini:
            if("ai:" in event.message.text[0:3]):
                # result=GeminiChatBot(event.message.text[3::])
                # user_message_text=event.message.text[3::]
                chat_history=get_chat_history(user_id)
                print(f"chat_history={chat_history}")

                formatted_history=""
                for entry in chat_history:
                    if entry['userId']==user_id:
                        formatted_history += f"User: {entry['messageText']}\n"
                    else:
                        formatted_history += f"Bot: {entry['messageText']}\n"
                    print(f"formatted_history={formatted_history}")

                ## 建立歷史紀錄prompt
                prompt_input=f"{formatted_history}User: {event.message.text[3:]}"
                print(f"prompt_input={prompt_input}")

                result=GeminiChatBot(prompt_input)
                
                print(f"ai result={result[0:]}")
                        
            else:
                result=event.message.text if "c:" in event.message.text[0:2] else ""

            
            
        elif event.message.type == 'image':
            message_pic=get_message_pic(event.message.id, os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
            image_path=os.path.join('pic','downloadimg.jpg')
            with open(image_path, 'wb') as f:
                for i in message_pic.iter_content():
                    f.write(i)

            print(f"picture saved")

            # result=send_image_to_AI(image_path) ## 傳給 AI LMStudio
            result=GeminiChatBot_pic()
        
        # 2025/02/06如果 result是空的話, linebot不處理訊息,
        if(result!=""):
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    # messages=[TextMessage(text=event.message.text)]
                    messages=[TextMessage(text=result)]
                )
            )
            print(f"{event.timestamp} msg from {event.source} : {event.message.text}")
        
        # 20250328
        # 新增：將使用者訊息發送到 Google Apps Script
        if GOOGLE_APPS_SCRIPT_URL:
            payload = {
                "timestamp": timestamp,
                "userId": user_id,
                "messageType": user_message_type,
                "messageText": user_message_text
            }
            try:
                headers = {'Content-Type': 'application/json'}
                time.sleep(0.25)  #加一個小延遲防止訊息傳進來太快 google app script來不及寫入 sheet.
                response = requests.post(GOOGLE_APPS_SCRIPT_URL, headers=headers, data=json.dumps(payload))
                response.raise_for_status() # 如果請求失敗會拋出異常
                print(f"訊息已成功發送到 Google Sheet. Status Code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"發送訊息到 Google Sheet 失敗: {e}")

if __name__ == '__main__':
    app.run(debug=True)
