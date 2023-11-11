from flask import Flask, request, jsonify
import datetime
from loader import dp, BOT_TOKEN, NGROK_URL
from dp.webhook import Webhook
from keyboards import reply_keyboards, inline_keyboards
from states.states import TestState

app = Flask(__name__)

@app.route("/getCountryList", methods=["GET"])
def get_country_list():
    timestamp = datetime.datetime.now().isoformat()
    countries = ["Argentina", "Russia"]
    data = {
        "timestamp": timestamp,
        "countries": countries
    }
    return jsonify(data)

@app.route("/setCountry", methods=["POST"])
def set_country():
    try:
        # Получаем JSON-данные из тела POST-запроса
        data = request.json

        # Проверяем, есть ли ключ "country" в JSON-данных
        if "country" in data:
            country = data["country"]
            # Выполняем действия с переменной "country", например, сохраняем ее в базу данных
            menu = []
            if country == 'Argentina':
                menu = ['documents','money change','transfer','translator']
            if country == 'Russia':
                menu = ['documents','transfer']
            # Возвращаем успешный ответ
            response = {
                "status": f"Country '{country}' successfully processed.",
                "menu": menu
            }
            return jsonify(response), 200
        else:
            # Если ключ "country" отсутствует в JSON-данных, возвращаем ошибку
            response = {"error": "Missing 'country' key in JSON data."}
            return jsonify(response), 400

    except Exception as e:
        # Если произошла ошибка при обработке запроса, возвращаем ошибку сервера
        response = {"error": str(e)}
        return jsonify(response), 500


@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        get_json = dp.get_json(request)

        if dp.message_handler(request, text="/start"):
            dp.send_message(
                chat_id=get_json["message"]["chat"]["id"],
                text=f"Hello {get_json['message']['chat']['first_name']}",
                reply_markup=reply_keyboards.btn_markup,
                variable_name="btn_markup"
            )
        # State
        if dp.message_handler(request, text="State🚥"):
            dp.send_message(
                chat_id=get_json["message"]["chat"]["id"],
                text="Enter your name: "
            )
            TestState.name.set()

        elif dp.message_handler(request, state=TestState.name.is_()):
            dp.send_message(
                chat_id=get_json["message"]["chat"]["id"],
                text="Ok.\nEnter your last name: "
            )
            # Name finish
            TestState.name.update(text=get_json["message"]["text"])
            TestState.name.finish()

            TestState.last_name.set()

        elif dp.message_handler(request, state=TestState.last_name.is_()):
            dp.send_message(
                chat_id=get_json["message"]["chat"]["id"],
                text="Ok"
            )
            TestState.last_name.update(text=get_json["message"]["text"])
            TestState.last_name.finish()
            # Send data
            msg = "Your information\n"
            msg += f"Name: {TestState.name.get()['name']}\n"
            msg += f"Last name: {TestState.last_name.get()['last_name']}"
            dp.send_message(
                chat_id=get_json["message"]["chat"]["id"],
                text=msg
            )

        # Content types
        if dp.message_handler(request, content_types="photo"):
            photo_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSEcNk1_0nuXOHHLECTgwQnLThcnvHnvNcHpJ7r-HTZ&s"
            dp.send_photo(
                chat_id=get_json["message"]["chat"]["id"],
                photo=photo_url,
                caption="<b>Photo</b>\nThis is a test image"
            )

        if dp.message_handler(request, content_types="video"):
            video_url = "https://dm0qx8t0i9gc9.cloudfront.net/watermarks/video/kx2d2Jf/extreme-close-up-view-of-clock-at-the-last-3-seconds-to-midnight_ejojcmqf__cf53370888a04095fe9a9410b8099739__P360.mp4"
            resp = dp.send_video(
                chat_id=get_json["message"]["chat"]["id"],
                video=video_url,
                caption="<b>Video</b>\nThis is a test video"
            )
            print(resp.json())

        # Callback data
        elif dp.callback_data(request, text="like"):
            dp.send_message(
                chat_id=get_json["callback_query"]["message"]["chat"]["id"],
                text="Thank you very much for the like.\nMy github portfolio: https://github.com/SarvarbekUzDev",
            )



    return {"Ok":True}

if __name__ == "__main__":
    # webhook
    Webhook(token=BOT_TOKEN).set_webhook(ngrok_url=NGROK_URL)
    # app run
    app.run(debug=True)
