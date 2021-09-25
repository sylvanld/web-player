import hashlib
import json
import sys
from base64 import b64decode
from functools import wraps
from json.decoder import JSONDecodeError
from os import environ

import requests
from flask import Flask, Response, redirect, render_template, request, url_for

try:
    USERNAME = environ["USERNAME"]
    PASSWORD_HASH = environ["PASSWORD_HASH"]
    VIDEO_SERVER_URL = environ["VIDEO_SERVER_URL"]
except KeyError as error:
    raise Exception("Missing the following environment variable: %s" % str(error))


def hash_password(plain_password: str) -> str:
    return hashlib.sha256(plain_password.encode("utf-8")).hexdigest()


def get_credentials():
    authz_header = request.headers.get("Authorization")
    if authz_header is None or not authz_header.startswith("Basic "):
        return None
    credentials = b64decode(authz_header[6:]).decode("utf-8").split(":")
    return {"username": credentials[0], "password": credentials[1]}


def basicauth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        credentials = get_credentials()
        if (
            credentials
            and credentials["username"] == USERNAME
            and hash_password(credentials["password"]) == PASSWORD_HASH
        ):
            return func(*args, **kwargs)
        return Response(
            "Merci de vous authentifier",
            headers={"WWW-Authenticate": "Basic realm=videoplayer"},
            status=401,
        )

    return wrapper


def get_videos():
    try:
        response = requests.get(VIDEO_SERVER_URL + "/manifest.json")
        return response.json()["videos"]
    except (requests.exceptions.ConnectionError, JSONDecodeError):
        return []


def get_video(filename):
    videos = get_videos()
    try:
        video = next(video for video in videos if video["filename"] == filename)
        video["absolute_url"] = VIDEO_SERVER_URL + "/" + filename
        return video
    except StopIteration:
        return None


app = Flask(__name__, static_folder="videos", static_url_path="/files/videos")


@app.route("/")
@basicauth
def dashboard():
    return redirect(url_for("browse_videos"))


@app.route("/videos")
@basicauth
def browse_videos():
    videos = get_videos()
    return render_template("browse_videos.html", videos=videos)


@app.route("/videos/<string:filename>")
@basicauth
def play_video(filename: str):
    return render_template("play_video.html", video=get_video(filename))
