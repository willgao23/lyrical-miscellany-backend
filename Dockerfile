FROM python:3.12-alpine

ENV GENIUS_ACCESS_TOKEN="Your Genius Access Token"

EXPOSE 5000/tcp

WORKDIR /src/

COPY /src/themes.txt .

COPY requirements.txt .

RUN apk add --update alpine-sdk

RUN pip install -r requirements.txt

COPY /src/app.py .

CMD [ "python", "./app.py" ]