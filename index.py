from flask import Flask, render_template, send_file, Response
import pymysql
import requests
from gtts import gTTS
import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras

app = Flask(__name__)

api_endpoint = "https://api.openweathermap.org/data/2.5/weather"
api_key = "e988dcd5742e41a5b9ca696d6d207115"

model1 = keras.models.load_model('static/detection2.h5')
model2 = keras.models.load_model('static/color3.h5')
model3 = keras.models.load_model('static/pattern2.h5')

class_names_model1 = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
                      'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

class_names_model2 = ['Black', 'Blue', 'Green', 'Pink', 'Red', 'White', 'Yellow']

class_names_model3 = ['Dot', 'Floral', 'Plain', 'Striped']

def generate_frames():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        input_frame = cv2.resize(frame, (28, 28))
        input_frame = cv2.cvtColor(input_frame, cv2.COLOR_BGR2GRAY)
        input_frame = input_frame / 255.0
        input_frame = np.expand_dims(input_frame, axis=0)
        predictions1 = model1.predict(input_frame)
        predicted_class1 = np.argmax(predictions1)
        class_name1 = class_names_model1[predicted_class1]

        input_frame_model2 = cv2.resize(frame, (224, 224))
        input_frame_model2 = cv2.cvtColor(input_frame_model2, cv2.COLOR_BGR2RGB)
        input_frame_model2 = input_frame_model2 / 255.0
        input_frame_model2 = np.expand_dims(input_frame_model2, axis=0)
        predictions2 = model2.predict(input_frame_model2)
        predicted_class2 = np.argmax(predictions2)
        class_name2 = class_names_model2[predicted_class2]

        input_frame_model3 = cv2.resize(frame, (224, 224))
        input_frame_model3 = cv2.cvtColor(input_frame_model3, cv2.COLOR_BGR2RGB)
        input_frame_model3 = input_frame_model3 / 255.0
        input_frame_model3 = np.expand_dims(input_frame_model3, axis=0)
        predictions3 = model3.predict(input_frame_model3)
        predicted_class3 = np.argmax(predictions3)
        class_name3 = class_names_model3[predicted_class3]

        cv2.putText(frame, f'Model 1: {class_name1}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'Model 2: {class_name2}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'Model 3: {class_name3}', (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
    cv2.destroyAllWindows()

@app.route('/')
def main_page():
    return render_template('main.html')

@app.route('/main1')
def main1():
    return render_template('main1.html')

@app.route('/main2')
def main2():
    return render_template('main2.html')

@app.route('/detection')
def main():
    return render_template('detection.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/index1')
def index1():
    return render_template('index1.html')

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
    return render_template('index2.html')

@app.route('/weather', methods=['GET'])
def weather():
    city = "Seoul"  # 날씨를 확인할 도시 이름을 설정합니다.
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

@app.route('/detection')
def detection():
    return render_template('detection.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/static/<path:filename>')
def static_file(filename):
    return send_file(filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)