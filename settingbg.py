
import os
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
load_dotenv()
configuration=os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(configuration)

with open('raspberry-pi-3-pinout-768x810.jpg', 'rb') as f:
    line_bot_api.set_rich_menu_image('richmenu-8daf7484861776735a0949a96a17e048', 'image/jpeg', f)

import requests

headers = {'Authorization':f'Bearer {configuration}'}

req = requests.request('POST', 'https://api.line.me/v2/bot/user/all/richmenu/richmenu-8daf7484861776735a0949a96a17e048', headers=headers)

print(req.text)