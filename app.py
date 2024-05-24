from flask import Flask
from lyricsgenius import Genius
import os
import math
import datetime

app = Flask(__name__)
genius = Genius(os.environ['GENIUS_ACCESS_TOKEN'])
daily_game_state = {}
current_theme_word_num = 0 

@app.get("/game")
def get_daily_game():
    if not (daily_game_state and datetime.date.today().strftime("%B %d, %Y") == daily_game_state["date"]):
        global current_theme_word_num
        theme_words = open('theme_words.txt')
        generate_daily_game(theme_words.readlines()[current_theme_word_num])
        current_theme_word_num += 1
    return daily_game_state

def generate_daily_game(theme):
    request = genius.search_lyrics(theme)
    daily_game_state.update({"date": datetime.date.today().strftime("%B %d, %Y")})
    daily_game_state.update({"songs": {}})
    for hit in request['sections'][0]['hits']:
        if len(daily_game_state["songs"]) >= 4:
            break
        title = hit['result']['full_title'].replace(u'\xa0', u' ')
        if title.count('Remix') == 0 and title.count('Romanized') == 0:
            lyrics =  hit['highlights'][0]['value'].lower()
            words = lyrics.split()
            counter = math.floor(len(words) / 4)
            grouped_words = [' '.join(words[i: i + counter]) for i in range(0, 3 * counter, counter)]
            grouped_words.append(' '.join(words[3 * counter:]))
            song_name = 'song_' + title[:3].upper()
            song = {"lyrics": grouped_words, "title": title}
            daily_game_state["songs"].update({song_name: song})
    return