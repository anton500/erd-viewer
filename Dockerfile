FROM python:3.9-slim

WORKDIR /usr/erd-viewer
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \ 
    && apt-get -qq update && apt-get -qq install graphviz -y \
    && rm -rf /var/lib/apt/lists/*

COPY erd-viewer/ erd-viewer/

ENTRYPOINT [ "python", "erd-viewer/main.py" ]