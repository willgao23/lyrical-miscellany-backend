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
RELEASE_DATE = date(2024, 6, 24)

@app.route("/game", methods=["POST", "OPTIONS"])
def get_daily_game():
    """
    Gets the game state for the given date 
    ---
    tags:
      - Lyrical Miscellany API
    parameters:
      - name: year
        in: query
        type: integer
        description: year to get the game state for
      - name: month
        in: query
        type: integer
        description: month to get the game state for
      - name: day
        in: query
        type: integer
        description: day to get the game state for
    responses:
      500:
        description: Internal server error
      200:
        description: The game state of the requested date
        schema:
          properties:
            date:
              type: string
              description: the date associated with the returned game state in \"month day, year\" format
            theme:
              type: string
              description: the theme of the returned game state
            songs:
              type: array
              description: a list of four formatted songs
              items:
                type: object
                fields:
                  lyrics:
                    type: array
                    description: a list of a section of a song's lyrics containing the daily theme, split into four and formatted
                    items:
                      type: string
                      description: a lyric section portion
                  title:
                    type: string
                    description: the title of the song
    """
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    elif request.method == "POST": 
        data = request.get_json(force=True)
        userDate = date(data["year"], data["month"], data["day"])
        if (not DAILY_GAME_STATE or DAILY_GAME_STATE["date"] != userDate.strftime("%B %d, %Y")):
            index = (userDate - RELEASE_DATE).days
            generate_daily_game(get_theme_word(index), userDate)
        return _corsify_actual_response(jsonify(DAILY_GAME_STATE))
    else:
        raise RuntimeError("Weird - don't know how to handle method {}".format(request.method))
    
def generate_daily_game(theme, date):
    '''
    Updates DAILY_GAME_STATE with a new game state created from the given theme
    '''
    request = search_genius_with_theme(theme)
    DAILY_GAME_STATE.update({"date": date.strftime("%B %d, %Y")})
    DAILY_GAME_STATE.update({"theme": theme})
    DAILY_GAME_STATE.update({"songs": []})
    songs_found = request['sections'][0]['hits']
    for song in songs_found:
        if len(DAILY_GAME_STATE["songs"]) >= 4:
            break
        title = censor(song['result']['full_title'].replace('\xa0', ' '), False)
        if title.count('Remix') == 0 and title.count('Romanized') == 0 and title.count('Chapter') == 0: # avoids duplicate songs and books from being used
            lyrics = song['highlights'][0]['value'].lower()
            censored_lyrics = censor(lyrics, True)
            words = censored_lyrics.split()
            words = words[1:len(words) - 1] # the Genius API often returns lyrics with partially cut-off first and last words, trimming for consistency
            counter = math.floor(len(words) / 4)
            formatted_lyrics = [' '.join(words[i: i + counter])
                             for i in range(0, 3 * counter, counter)]
            formatted_lyrics.append(' '.join(words[3 * counter:]))
            song = {"lyrics": formatted_lyrics, "title": title}
            DAILY_GAME_STATE["songs"].append(song)

def censor(string, isLyric):
    '''
    Censors a given string 
    If isLyric is true, reformat string by adding back a newline character at the end of every line
    '''
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

def get_theme_word(index):
    '''
    Read and return the theme words from themes.txt at given index's line number
    '''
    with open('themes.txt', encoding="utf-8") as file:
        themes = file.readlines()
        formatted_theme = themes[index].replace("\n", "")
        return formatted_theme

def search_genius_with_theme(theme):
    '''
    Use the Genius Lyrics API to search for lyrics containing the theme word(s)
    Primarily a utility method so that the Genius API response can be mocked in unit testing
    '''
    return genius.search_lyrics(theme)

def get_daily_game_state():
    '''
    A utility method to retrieve the current game state
    '''
    return DAILY_GAME_STATE

def _build_cors_preflight_response():
    '''
    Add the necessary CORS headers when a preflight request is made
    '''
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(response):
    '''
    Add the neccessary CORS header to the response
    '''
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)