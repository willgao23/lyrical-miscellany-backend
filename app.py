import os
import math
import datetime

from flask import Flask
from lyricsgenius import Genius

app = Flask(__name__)
genius = Genius(os.environ['GENIUS_ACCESS_TOKEN'])
DAILY_GAME_STATE = {}
CURRENT_THEME_NUM = 0

@app.get("/game")
def get_daily_game():
    if not (DAILY_GAME_STATE and
            datetime.date.today().strftime("%B %d, %Y") == DAILY_GAME_STATE["date"]):
        global CURRENT_THEME_NUM
        with open('themes.txt', encoding="utf-8") as file:
            themes = file.readlines()
            generate_daily_game(themes[CURRENT_THEME_NUM])
            CURRENT_THEME_NUM += 1
    return DAILY_GAME_STATE

def generate_daily_game(theme):
    request = genius.search_lyrics(theme)
    DAILY_GAME_STATE.update({"date": datetime.date.today().strftime("%B %d, %Y")})
    DAILY_GAME_STATE.update({"songs": {}})
    for hit in request['sections'][0]['hits']:
        if len(DAILY_GAME_STATE["songs"]) >= 4:
            break
        title = hit['result']['full_title'].replace('\xa0', ' ')
        if title.count('Remix') == 0 and title.count('Romanized') == 0:
            lyrics =  hit['highlights'][0]['value'].lower()
            words = lyrics.split()
            counter = math.floor(len(words) / 4)
            grouped_words = [' '.join(words[i: i + counter])
                             for i in range(0, 3 * counter, counter)]
            grouped_words.append(' '.join(words[3 * counter:]))
            song_name = 'song_' + title[:3].upper()
            song = {"lyrics": grouped_words, "title": title}
            DAILY_GAME_STATE["songs"].update({song_name: song})
