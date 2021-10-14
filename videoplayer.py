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
    VIDEOS_SERVER_URL = environ["VIDEOS_SERVER_URL"]
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


def get_manifest():
    try:
        response = requests.get(VIDEOS_SERVER_URL + "/manifest.json")
        return response.json()
    except (requests.exceptions.ConnectionError, JSONDecodeError):
        return {}


def get_categories():
    return get_manifest().get("categories", [])


def get_category(category_path: str):
    for category in get_categories():
        if category["path"] == category_path:
            return category
    return None


def get_video(category_path: str, filename: str):
    category = get_category(category_path)
    videos = category["videos"]
    
    try:
        video = next(video for video in videos if video["filename"] == filename)
        video["absolute_url"] = VIDEOS_SERVER_URL + "/" + category_path + "/" + filename
        video["category_title"] = category["title"]
        return video
    except StopIteration:
        return None


def url_for_thumbnail(category_path: str):
    return VIDEOS_SERVER_URL + "/" + category_path + "/thumbnail.png"


app = Flask(__name__, static_folder="videos", static_url_path="/files/videos")


@app.route("/")
@basicauth
def dashboard():
    return redirect(url_for("browse_videos"))


@app.route("/videos")
@basicauth
def browse_videos():
    categories = get_categories()
    return render_template("browse_videos.html", categories=categories, url_for_thumbnail=url_for_thumbnail)


@app.route("/videos/<string:category_path>/<string:filename>")
@basicauth
def play_video(category_path: str, filename: str):
    return render_template("play_video.html", video=get_video(category_path, filename))
