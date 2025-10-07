# LINEBOT (with GEMINI chat bot system)
## 2025/09/02 重新抽換 GeminiChatBot中使用模型, 2.0-flash-exp已經不能用我的 api key, 而此種呼叫 api 方式可能年底2025/11月 SDK改版會變動, 需要改寫. 收換版 commit: 2bee3f5 



## 2025/08/08 加入 keepalive 機制.

## 2025/03/30 串接 Gemini 與 google sheet有記憶功能(前5筆使用者訊息)

## 2025/03/28 串接 google sheet達成書籤功能

## 2025/02/06 串接 Genimi

## 2025/01/21 串接 LMStudio

## Line Developer: https://developers.line.biz/en/
## 用 python寫的 LineBot service [flask web server] 
---
### port: 5000
### 將利用 devtunnel做內網穿透提供服務.
### 環境 .env會要在自己建入專案跟目錄中, 不會推送到 github.
### 預計是部署到 Render.com

