FROM python:3.9-alpine

WORKDIR /usr/erd-viewer
COPY requirements.txt ./
COPY erd-viewer/ erd-viewer/

RUN pip install --no-cache-dir -r requirements.txt

RUN apk add --no-cache graphviz

ENTRYPOINT [ "python", "erd-viewer/main.py" ]