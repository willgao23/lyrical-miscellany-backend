import os
import math
from datetime import date

from flask import Flask, request, jsonify, make_response
from waitress import serve
from lyricsgenius import Genius
from profanity_check import predict_prob

app = Flask(__name__)
genius = Genius(os.environ['GENIUS_ACCESS_TOKEN'])
DAILY_GAME_STATE = {}
STARTING_DATE = date(2024, 6, 24)

@app.route("/game", methods=["POST", "OPTIONS"])
def get_daily_game():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    elif request.method == "POST": 
        data = request.get_json(force=True)
        userDate = date(data["year"], data["month"], data["day"])
        if (not DAILY_GAME_STATE or DAILY_GAME_STATE["date"] != userDate.strftime("%B %d, %Y")):
            index = (userDate - STARTING_DATE).days
            generate_daily_game(get_theme_word(index), userDate)
        return _corsify_actual_response(jsonify(DAILY_GAME_STATE))
    else:
        raise RuntimeError("Weird - don't know how to handle method {}".format(request.method))
    
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
            lyrics = censor(hit['highlights'][0]['value'].lower())
            words = lyrics.split()
            words = words[1:len(words) - 1]
            counter = math.floor(len(words) / 4)
            grouped_words = [' '.join(words[i: i + counter])
                             for i in range(0, 3 * counter, counter)]
            grouped_words.append(' '.join(words[3 * counter:]))
            song = {"lyrics": grouped_words, "title": title}
            DAILY_GAME_STATE["songs"].append(song)

def censor(string, isLyric):
    line_array = string.split("\n")
    censored_string = ""
    for i in range(len(line_array)):
        word_array = line_array[i].split()
        profanity_check = predict_prob(word_array)
        censored_section = ""
        for j in range(len(word_array)):
            if profanity_check[j] > 0.9:
                censored_section += "****"
            else:
                censored_section += word_array[j]
            if (j != len(word_array) - 1):
                censored_section += " "
        censored_string += censored_section
        if (i != len(line_array) - 1) and isLyric:
            censored_string += "\n"
    return censored_string

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

def get_theme_word(index):
    with open('themes.txt', encoding="utf-8") as file:
        themes = file.readlines()
        formatted_theme = themes[index].replace("\n", "")
        return formatted_theme

def search_genius_with_theme(theme):
    return genius.search_lyrics(theme)

def get_daily_game_state():
    return DAILY_GAME_STATE

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)