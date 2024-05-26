from datetime import date

import src.app

def test_get_daily_game_todays_game_state_exists_return_existing(mocker, client):
    # Arrange
    mock_daily_game_state = {"date": "May 25, 2024", "songs": {}}
    mocker.patch("src.app.get_today", return_value = date(2024, 5, 25))
    mocker.patch("src.app.DAILY_GAME_STATE", new=mock_daily_game_state)
    mocker.patch("src.app.CURRENT_THEME_NUM", new=0)
    spy_game_generator = mocker.spy(src.app, "generate_daily_game")

    # Act
    response = client.get("/game")

    # Assert
    assert response.status_code == 200
    assert response.get_json() == mock_daily_game_state
    assert spy_game_generator.call_count == 0

def test_get_daily_game_no_daily_game_state_generate_new(mocker, client):
    # Arrange
    mocker.patch("src.app.get_today", return_value = date(2024, 5, 25))
    mocker.patch("src.app.get_theme_word", return_value = "mockTheme")
    mocker.patch("src.app.DAILY_GAME_STATE", new={})
    mocker.patch("src.app.CURRENT_THEME_NUM", new=0)
    spy_game_generator = mocker.spy(src.app, "generate_daily_game")
    spy_increment = mocker.spy(src.app, "increment_current_theme_num")

    # Act
    response = client.get("/game")

    # Assert
    assert response.status_code == 200
    assert spy_game_generator.call_count == 1
    assert spy_increment.call_count == 1
    spy_game_generator.assert_called_with("mockTheme")

def test_get_daily_game_new_day_generate_new(mocker, client):
    # Arrange
    mock_daily_game_state = {"date": "May 25, 2024", "songs": {}}
    mocker.patch("src.app.get_today", return_value = date(2024, 5, 26))
    mocker.patch("src.app.get_theme_word", return_value = "mockTheme")
    mocker.patch("src.app.DAILY_GAME_STATE", new=mock_daily_game_state)
    mocker.patch("src.app.CURRENT_THEME_NUM", new=0)
    spy_game_generator = mocker.spy(src.app, "generate_daily_game")
    spy_increment = mocker.spy(src.app, "increment_current_theme_num")

    # Act
    response = client.get("/game")

    # Assert
    assert response.status_code == 200
    assert spy_game_generator.call_count == 1
    assert spy_increment.call_count == 1
    spy_game_generator.assert_called_with("mockTheme")

def test_get_daily_game_exception_raised(mocker, client):
    # Arrange
    mocker.patch("src.app.get_today", return_value = date(2024, 5, 25))
    mocker.patch("src.app.get_theme_word", return_value = "mockTheme")
    mocker.patch("src.app.DAILY_GAME_STATE", new={})
    mocker.patch("src.app.CURRENT_THEME_NUM", new=0)
    mocker.patch("src.app.generate_daily_game", side_effect=Exception("Error"))

    # Act
    response = client.get("/game")

    # Assert
    assert response.status_code == 500

def test_generate_daily_game_success(mocker):
    # Arrange
    song_one = {'result':{'full_title':"One\xa0Title"},
                'highlights':[{'value':"first test one two three last"}]}
    song_remix = {'result':{'full_title':"Remix\xa0One"},
                  'highlights':[{'value':"first test one two three last"}]}
    song_romanized = {'result':{'full_title':"Romanized\xa0One"},
                      'highlights':[{'value':"first test one two three last"}]}
    song_two = {'result':{'full_title':"Two\xa0Title"},
                'highlights':[{'value':"first Test, Four! Five? Six() last"}]}
    song_three = {'result':{'full_title':"Three\xa0Title"},
                'highlights':[{'value':"first test seven eight nine ten eleven twelve last"}]}
    song_four = {'result':{'full_title':"Four\xa0Title"},
                'highlights':[{'value':"first test thirteen fourteen fifteen sixteen "
                               + "seventeen eighteen nineteen twenty last"}]}
    song_five = {'result':{'full_title':"Five\xa0Title"},
                'highlights':[{'value':"first test twenty-one twenty-two twenty-three last"}]}
    mock_genius_search_return = {'sections':[{'hits':[song_one,
                                                      song_remix,
                                                      song_two,
                                                      song_three,
                                                      song_romanized,
                                                      song_four,
                                                      song_five]}]}
    expected_song_one = {'lyrics':["test", "one", "two", "three"],
                         'title':"One Title"}
    expected_song_two = {'lyrics':["test,", "four!", "five?", "six()"],
                         'title':"Two Title"}
    expected_song_three = {'lyrics':["test", "seven", "eight", "nine ten eleven twelve"],
                           'title':"Three Title"}
    expected_song_four = {'lyrics':["test thirteen",
                                    "fourteen fifteen",
                                    "sixteen seventeen",
                                    "eighteen nineteen twenty"],
                          'title':"Four Title"}
    expected_game_state = {'date':'May 24, 2024',
                           'songs':{'song_ONE':expected_song_one,
                                    'song_TWO':expected_song_two,
                                    'song_THR':expected_song_three,
                                    'song_FOU':expected_song_four}}
    mocker.patch("src.app.get_today", return_value = date(2024, 5, 24))
    mocker.patch("src.app.search_genius_with_theme", return_value=mock_genius_search_return)

    # Act
    src.app.generate_daily_game("test")

    # Assert
    assert src.app.get_daily_game_state() == expected_game_state
