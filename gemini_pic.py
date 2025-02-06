from google import genai
from google.genai import types

import requests
import os
import PIL.Image

# 要讀 .env內容進來到環境變數, 這樣才吃得到 api_key:
from dotenv import load_dotenv
load_dotenv()

# 原來的範例是 網路圖片:
#image_path = "https://goo.gle/instrument-img"
#image = requests.get(image_path)

# 改本地端載入影像:
image_path="pic/downloadimg.jpg"
image=PIL.Image.open(image_path)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    # 原始範例:
    # contents=["What is this image?",
    #           types.Part.from_bytes(image.content, "image/jpeg")])
    contents=["What is this image?",
              image])
print(response.text)