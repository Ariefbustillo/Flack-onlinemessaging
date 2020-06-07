import os

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, send

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

channels = []
messages = {}

# main page
@app.route("/")
def index():
    return render_template("index.html")


# channel pages
@app.route("/channel/<channel_name>", methods=["GET"])
def channel(channel_name):
    return render_template("channel.html", channel_name=channel_name)


# add channel to channels variable
@app.route("/create_channel", methods=["post"])
def create_channel():
    channel_name = request.form.get("channel_name")
    channels.append(channel_name)
    messages.update({channel_name: []})
    # return channels as JSON
    context = jsonify({"channels": channels})
    return context


# sends channels as JSON
@app.route("/get_channels", methods=["GET"])
def get_channels():
    context = jsonify({"channels": channels})
    return context

# sends messages as JSON
@app.route("/get_messages", methods=["GET"])
def get_messages():
    context = jsonify({"messages": messages})
    return context


@socketio.on("join")
def join(data):
    channel = data["channel"]
    join_room(channel)


# define socket
@socketio.on("send_message")
def send_message(data):
    # get message
    message = data["message"]
    display_name = data["display_name"]
    room = data["channel"]
    # input message into global variable
    messages[room].append((display_name, message))
    # delete messages after the 100th message
    if len(messages[room]) > 100:
        messages[room].remove(messages[room][0])
    # emit message
    emit(
        "announce_message",
        {"message": message, "display_name": display_name, "channel": room},
        room=room,
    )
