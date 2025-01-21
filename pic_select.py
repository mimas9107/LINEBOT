import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()
configuration=os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
# 設定 headers，輸入你的 Access Token，記得前方要加上「Bearer 」( 有一個空白 )
headers = {'Authorization':f'Bearer {configuration}','Content-Type':'application/json'}
print(configuration)
body = {
  "size": {
    "width": 2500,
    "height": 1686
  },
  "selected": "true",
  "name": "圖文選單 1",
  "chatBarText": "查看更多資訊",
  "areas": [
    {
      "bounds": {
        "x": 411,
        "y": 235,
        "width": 706,
        "height": 185
      },
      "action": {
        "type": "message",
        "text": "3.3V"
      }
    },
    {
      "bounds": {
        "x": 1436,
        "y": 233,
        "width": 670,
        "height": 186
      },
      "action": {
        "type": "message",
        "text": "5V"
      }
    },
    {
      "bounds": {
        "x": 1424,
        "y": 983,
        "width": 695,
        "height": 106
      },
      "action": {
        "type": "message",
        "text": "GND"
      }
    },
    {
      "bounds": {
        "x": 1432,
        "y": 500,
        "width": 674,
        "height": 140
      },
      "action": {
        "type": "message",
        "text": "GND"
      }
    }
  ]
}
# 向指定網址發送 request
req = requests.request('POST', 'https://api.line.me/v2/bot/richmenu',
                      headers=headers,data=json.dumps(body).encode('utf-8'))
# 印出得到的結果
print(req.text)