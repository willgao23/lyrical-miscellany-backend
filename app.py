from flask import Flask
from lyricsgenius import Genius
import os
import math

app = Flask(__name__)
genius = Genius(os.environ['GENIUS_ACCESS_TOKEN'])

daily_game_state = {}

@app.get("/game")
def get_daily_game():
    return daily_game_state

def generate_daily_game(theme):
    request = genius.search_lyrics(theme)
    for hit in request['sections'][0]['hits']:
        if len(daily_game_state) >= 4:
            break
        title = hit['result']['full_title'].replace(u'\xa0', u' ')
        # Prevents the inclusion of duplicates from translations / remixes
        if (title.count('(') == 0):
            lyrics =  hit['highlights'][0]['value'].lower()
            words = lyrics.split()
            counter = math.ceil(len(words) / 4)
            grouped_words = [' '.join(words[i: i + counter]) for i in range(0, len(words), counter)]
            song_name = 'song_' + title[:3].upper()
            song = {"lyrics": grouped_words, "title": title}
            daily_game_state.update({song_name: song})
    return