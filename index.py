from flask import Flask, render_template, send_file
import pymysql
import requests
from gtts import gTTS
import os

app = Flask(__name__)

api_endpoint = "https://api.openweathermap.org/data/2.5/weather"
api_key = "e988dcd5742e41a5b9ca696d6d207115"

@app.route('/')

def index():
    db = pymysql.connect(host="localhost", user="root", passwd="rlaskskdud10231!", db="free_board", charset="utf8")
    cur = db.cursor()

    sql = "SELECT * from board"
    cur.execute(sql)

    data_list = cur.fetchall()
    return render_template('index.html', data_list=data_list)

@app.route('/index1')
def index1():
    db = pymysql.connect(host="localhost", user="root", passwd="rlaskskdud10231!", db="free_board", charset="utf8")
    cur = db.cursor()

    sql = "SELECT * from board"
    cur.execute(sql)

    data_list = cur.fetchall()
    return render_template('index1.html', data_list=data_list)

def get_weather_code(city):
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "kr"
    }

    response = requests.get(api_endpoint, params=params)
    data = response.json()

    if data.get("cod") == 200:
        weather_code = data["weather"][0]["id"]
    else:
        weather_code = None

    return weather_code

@app.route('/index2')
def index2():
    db = pymysql.connect(host="localhost", user="root", passwd="rlaskskdud10231!", db="free_board", charset="utf8")
    cur = db.cursor()

    sql = "SELECT * from board"
    cur.execute(sql)

    data_list = cur.fetchall()
    return render_template('index2.html', data_list=data_list)

@app.route('/index3')
def index3():
    db = pymysql.connect(host="localhost", user="root", passwd="rlaskskdud10231!", db="free_board", charset="utf8")
    cur = db.cursor()

    sql = "SELECT * from board"
    cur.execute(sql)

    data_list = cur.fetchall()
    return render_template('index3.html', data_list=data_list)

@app.route('/weather', methods=['GET'])
def weather():
    city = "Busan"  # 날씨를 확인할 도시 이름을 설정합니다.
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "kr"
    }

    response = requests.get(api_endpoint, params=params)
    data = response.json()

    if data.get("cod") == 200:
        weather_description = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
    else:
        weather_description = "날씨 정보 없음"
        temperature = 0
        humidity = 0
        
    # TTS로 음성 생성
    text = f"현재 {city}의 날씨는 {weather_description}이며, 온도는 {temperature} ℃이고 습도는 {humidity} %입니다."
    tts = gTTS(text=text, lang='ko', slow=False)

    # 생성된 TTS를 파일로 저장
    audio_file_path = "static/weather_tts.mp3"
    tts.save(audio_file_path)

    weather_code = get_weather_code(city)

    return render_template('weather.html', tts_file=audio_file_path, city=city, description=weather_description, temperature=temperature, humidity=humidity)

@app.route('/static/<path:filename>')
def static_file(filename):
    return send_file(filename)

@app.route('/write')
def write():
    return render_template('write.html')

if __name__ == '__main__':
    app.run()