FROM python:3.9-slim

WORKDIR /usr/erd-viewer
COPY . .

RUN pip install --no-cache-dir -r requirements.txt \ 
    && apt-get -qq update && apt-get -qq install graphviz -y \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT [ "python", "erd-viewer/main.py" ]