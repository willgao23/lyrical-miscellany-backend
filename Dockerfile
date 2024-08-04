FROM python:latest

ENV GENIUS_ACCESS_TOKEN="Your Genius Access Token"

EXPOSE 5000/tcp

WORKDIR /src/

COPY /src/themes.txt .

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY /src/app.py .

CMD [ "python", "./app.py" ]