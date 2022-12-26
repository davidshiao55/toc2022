import os
import sys
import re
from SpotifyAPI import SpotifyAPI

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

from fsm import TocMachine

load_dotenv()

spotify = SpotifyAPI()

machine = TocMachine(
    states=["user", "state1", "state2", "state3"],
    transitions=[
        {
            "trigger": "advance",
            "source": ["user", "state2", "state3"],
            "dest": "state1",
            "conditions": "is_going_to_state1",
        },
        {
            "trigger": "advance",
            "source": ["user", "state1", "state3"],
            "dest": "state2",
            "conditions": "is_going_to_state2",
        },
        {
            "trigger": "advance",
            "source": ["state1", "state2", "state3"],
            "dest": "user",
            "conditions": "is_going_to_user",
        },
        {
            "trigger": "advance",
            "source": ["user", "state1", "state2"],
            "dest": "state3",
            "conditions": "is_going_to_state3"
        }
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, message_handler(text=event.message.text)
        )

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if response == False:
            line_bot_api.reply_message(
                event.reply_token, message_handler(text=event.message.text)
            )
        else:
            if machine.state_text == "USER":
                line_bot_api.reply_message(
                    event.reply_token, get_user_button())
            elif machine.state_text == "BILLBOARD":
                line_bot_api.reply_message(
                    event.reply_token, get_chart_button())
            else:
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(
                        text=machine.welcome_message())
                )

    return "OK"


def message_handler(text):
    if re.match(text.lower(), "help"):
        return TextSendMessage(
            text=machine.help_text())

    if (machine.state_text == "SEARCH"):
        if re.match(text.lower(), "preview"):
            preview_url = spotify.preview_track()
            return TextSendMessage(text=preview_url)
        elif re.match(text.lower(), "next"):
            spotify.search_next_track()
            return get_song_button()
        else:
            spotify.search_tracks(text)
            return get_song_button()

    elif (machine.state_text == "ARTIST"):
        if re.match(text.lower(), "next"):
            spotify.get_artist_top_track_next()
            return get_song_button()
        elif re.match(text.lower(), "next artist"):
            spotify.search_next_artist()
            return get_artist_button()
        elif re.match(text.lower(), "top"):
            spotify.get_artist_top_track()
            return get_song_button()
        elif re.match(text.lower(), "preview"):
            preview_url = spotify.preview_track()
            return TextSendMessage(text=preview_url)
        spotify.search_artist(text)
        return get_artist_button()

    elif (machine.state_text == "USER"):
        if re.match(text.lower(), "random"):
            spotify.get_random_track_url_from_myplaylist()
            return get_song_button()
        elif re.match(text.lower(), "preview"):
            preview_url = spotify.preview_track()
            return TextSendMessage(text=preview_url)
        elif re.match(text.lower(), "next"):
            spotify.get_random_track_url_from_myplaylist()
            return get_song_button()
        else:
            return get_user_button()

    elif (machine.state_text == "BILLBOARD"):
        flag = True
        try:
            # try converting to integer
            int(text)
        except ValueError:
            flag = False
        if flag:
            spotify.billboard_load_track(int(text))
            return get_song_button()
        elif re.match(text.lower(), "chart"):
            return TextSendMessage(text=spotify.billboard_chart())
        elif re.match(text.lower(), "next"):
            spotify.billboard_load_next()
            return get_song_button()
        elif re.match(text.lower(), "random"):
            spotify.billboard_load_random()
            return get_song_button()
        else:
            return get_chart_button()


def get_user_button():
    button_template_message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            thumbnail_image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/347121297/android/sticker.png',
            title='SPOTIFY BOT',
            text='Please select',
            actions=[
                MessageAction(
                    label='search track',
                    text='track'
                ),
                MessageAction(
                    label='search artist',
                    text='artist'
                ),
                MessageAction(
                    label='billboard chart',
                    text='billboard'
                ),
                MessageAction(
                    label='song for you',
                    text='random'
                )
            ]
        )
    )
    return button_template_message


def get_chart_button():
    button_template_message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            thumbnail_image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/347121299/android/sticker.png',
            title='BillBoard chart',
            text='Enter number to load the ranking track',
            actions=[
                MessageAction(
                    label='Top 20 chart',
                    text='chart'
                ),

                MessageAction(
                    label='random song',
                    text='random'
                ),
                MessageAction(
                    label='exit',
                    text='exit'
                )
            ]
        )
    )
    return button_template_message


def get_song_button():
    button_template_message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            thumbnail_image_url=spotify.get_album_cover_art(),
            title=spotify.get_curr_track_name(),
            text=spotify.get_curr_track_artist(),
            actions=[
                MessageAction(
                    label='preview',
                    text='preview'
                ),
                MessageAction(
                    label='next',
                    text='next'
                ),
                URIAction(
                    label='spotify link',
                    uri=spotify.get_curr_track_url()
                )
            ]
        )
    )
    return button_template_message


def get_artist_button():
    button_template_message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            thumbnail_image_url=spotify.get_curr_artist_image(),
            title=spotify.get_curr_artist_name(),
            text=spotify.get_curr_artist_genre(),
            actions=[
                MessageAction(
                    label='top track',
                    text='top'
                ),
                MessageAction(
                    label='next artist',
                    text='next artist'
                ),
                URIAction(
                    label='spotify link',
                    uri=spotify.get_curr_artist_url()
                )
            ]
        )
    )
    return button_template_message


@ app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("img/fsm.png", prog="dot", format="png")
    return send_file("img/fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
