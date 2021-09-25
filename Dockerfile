FROM python:3.8-alpine

WORKDIR /videoplayer

COPY requirements /tmp/requirements
RUN pip install --no-cache-dir -r /tmp/requirements && rm /tmp/requirements

COPY videoplayer.py /videoplayer/videoplayer.py
COPY templates/ /videoplayer/templates/

CMD [ "gunicorn", "-b", "0.0.0.0:80", "videoplayer:app"]