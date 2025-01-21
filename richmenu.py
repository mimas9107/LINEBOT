# -*- coding: utf-8 -*-

import os
import sys

from dotenv import load_dotenv

from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    RichMenuRequest,
    RichMenuArea,
    RichMenuSize,
    RichMenuBounds,
    MessageAction,
    URIAction,
    RichMenuSwitchAction,
    CreateRichMenuAliasRequest
)

channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

configuration = Configuration(
    access_token=channel_access_token
)


def rich_menu_object_a_json():
    return {
  "size": {
    "width": 2500,
    "height": 1686
  },
  "selected": True,
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


# def rich_menu_object_b_json():
#     return {
#         "size": {
#             "width": 2500,
#             "height": 1686
#         },
#         "selected": False,
#         "name": "richmenu-b",
#         "chatBarText": "Tap to open",
#         "areas": [
#             {
#                 "bounds": {
#                     "x": 0,
#                     "y": 0,
#                     "width": 1250,
#                     "height": 1686
#                 },
#                 "action": {
#                     "type": "richmenuswitch",
#                     "richMenuAliasId": "richmenu-alias-a",
#                     "data": "richmenu-changed-to-a"
#                 }
#             },
#             {
#                 "bounds": {
#                     "x": 1251,
#                     "y": 0,
#                     "width": 1250,
#                     "height": 1686
#                 },
#                 "action": {
#                     "type": "uri",
#                     "uri": "https://www.line-community.me/"
#                 }
#             }
#         ]
#     }

## 修改點選以後的動作:
def create_action(action):
    # if action['type'] == 'uri':
    #     return URIAction(uri=action.get('uri'))
    # else:
    #     return RichMenuSwitchAction(
    #         rich_menu_alias_id=action.get('richMenuAliasId'),
    #         data=action.get('data')
    #     )
    if action['type'] == 'message':
        return MessageAction(text=action.get('text'))
        # pass


def main():
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_blob_api = MessagingApiBlob(api_client)

        # 2. Create rich menu A (richmenu-a)
        rich_menu_object_a = rich_menu_object_a_json()
        areas = [
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=info['bounds']['x'],
                    y=info['bounds']['y'],
                    width=info['bounds']['width'],
                    height=info['bounds']['height']
                ),
                action=create_action(info['action'])
            ) for info in rich_menu_object_a['areas']
        ]

        rich_menu_to_a_create = RichMenuRequest(
            size=RichMenuSize(width=rich_menu_object_a['size']['width'],
                              height=rich_menu_object_a['size']['height']),
            selected=rich_menu_object_a['selected'],
            name=rich_menu_object_a['name'],
            chat_bar_text=rich_menu_object_a['name'],
            areas=areas
        )

        rich_menu_a_id = line_bot_api.create_rich_menu(
            rich_menu_request=rich_menu_to_a_create
        ).rich_menu_id

        # 3. Upload image to rich menu A
        with open('./pic/line-rich-menu-demo.jpg', 'rb') as image:
            line_bot_blob_api.set_rich_menu_image(
                rich_menu_id=rich_menu_a_id,
                body=bytearray(image.read()),
                _headers={'Content-Type': 'image/png'}
            )
        # =================== 只有設定作用在 menu A
        # # 4. Create rich menu B (richmenu-b)
        # rich_menu_object_b = rich_menu_object_b_json()
        # areas = [
        #     RichMenuArea(
        #         bounds=RichMenuBounds(
        #             x=info['bounds']['x'],
        #             y=info['bounds']['y'],
        #             width=info['bounds']['width'],
        #             height=info['bounds']['height']
        #         ),
        #         action=create_action(info['action'])
        #     ) for info in rich_menu_object_b['areas']
        # ]

        # rich_menu_to_b_create = RichMenuRequest(
        #     size=RichMenuSize(width=rich_menu_object_b['size']['width'],
        #                       height=rich_menu_object_b['size']['height']),
        #     selected=rich_menu_object_b['selected'],
        #     name=rich_menu_object_b['name'],
        #     chat_bar_text=rich_menu_object_b['name'],
        #     areas=areas
        # )

        # rich_menu_b_id = line_bot_api.create_rich_menu(
        #     rich_menu_request=rich_menu_to_b_create
        # ).rich_menu_id

        # 5. Upload image to rich menu B
        # with open('./pic/richmenu-b.png', 'rb') as image:
        #     line_bot_blob_api.set_rich_menu_image(
        #         rich_menu_id=rich_menu_b_id,
        #         body=bytearray(image.read()),
        #         _headers={'Content-Type': 'image/png'}
        #     )

        # 6. Set rich menu A as the default rich menu
        line_bot_api.set_default_rich_menu(rich_menu_id=rich_menu_a_id)

        # # 7. Create rich menu alias A
        # alias_a = CreateRichMenuAliasRequest(
        #     rich_menu_alias_id='richmenu-alias-a',
        #     rich_menu_id=rich_menu_a_id
        # )
        # line_bot_api.create_rich_menu_alias(alias_a)

        # # 8. Create rich menu alias B
        # alias_b = CreateRichMenuAliasRequest(
        #     rich_menu_alias_id='richmenu-alias-b',
        #     rich_menu_id=rich_menu_b_id
        # )
        # line_bot_api.create_rich_menu_alias(alias_b)
        print('success')

load_dotenv()
main()