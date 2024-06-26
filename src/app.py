import os
import math
from datetime import date

from flask import Flask, request
from waitress import serve
from lyricsgenius import Genius

app = Flask(__name__)
genius = Genius(os.environ['GENIUS_ACCESS_TOKEN'])
DAILY_GAME_STATE = {}
STARTING_DATE = date(2024, 6, 25)

@app.post("/game")
def get_daily_game():
    data = request.get_json(force=True)
    userDate = date(data["year"], data["month"], data["day"])
    if (not DAILY_GAME_STATE or DAILY_GAME_STATE["date"] != date):
        index = (userDate - STARTING_DATE).days
        generate_daily_game(get_theme_word(index), userDate)
    return DAILY_GAME_STATE

def generate_daily_game(theme, date):
    request = search_genius_with_theme(theme)
    DAILY_GAME_STATE.update({"date": date.strftime("%B %d, %Y")})
    DAILY_GAME_STATE.update({"theme": theme})
    DAILY_GAME_STATE.update({"songs": []})
    for hit in request['sections'][0]['hits']:
        if len(DAILY_GAME_STATE["songs"]) >= 4:
            break
        title = hit['result']['full_title'].replace('\xa0', ' ')
        if title.count('Remix') == 0 and title.count('Romanized') == 0 and title.count('Chapter') == 0:
            lyrics =  hit['highlights'][0]['value'].lower()
            words = lyrics.split()
            words = words[1:len(words) - 1]
            counter = math.floor(len(words) / 4)
            grouped_words = [' '.join(words[i: i + counter])
                             for i in range(0, 3 * counter, counter)]
            grouped_words.append(' '.join(words[3 * counter:]))
            song = {"lyrics": grouped_words, "title": title}
            DAILY_GAME_STATE["songs"].append(song)

def get_theme_word(index):
    with open('themes.txt', encoding="utf-8") as file:
        themes = file.readlines()
        return themes[index]

def search_genius_with_theme(theme):
    return genius.search_lyrics(theme)

def get_daily_game_state():
    return DAILY_GAME_STATE

if __name__ == "__main__":
   serve(app, host='0.0.0.0', port=5000)
