import asyncio
import json
import threading
from flask import Flask, jsonify
from nats.aio.client import Client as NATS

app = Flask(__name__)
# Сховище для даних гільдії
guild_data = {"last_update": "waiting", "members": []}

async def nats_listener():
    nc = NATS()
    try:
        # Підключаємось до знайденого тобою сервера
        await nc.connect("nats://public:thenewalbiondata@nats.albion-online-data.com:34222")
        print("Connected to Albion NATS!")

        async def message_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                # Фільтруємо дані: шукаємо оновлення списків гільдій
                # Albion Data Project зазвичай надсилає масиви об'єктів
                if isinstance(data, list):
                    for item in data:
                        if item.get("GuildId") == "wa7AF_VWSqiUxQBRI-VAXw":
                            guild_data["members"] = item.get("Members", [])
                            guild_data["last_update"] = "OK"
            except Exception as e:
                print(f"Error parsing message: {e}")

        # Підписуємось на топік з гільдіями
        await nc.subscribe("goldprices", cb=message_handler) # Для тесту можна спробувати загальні топіки
        await asyncio.Future() 
    except Exception as e:
        print(f"NATS Connection error: {e}")

def start_nats():
    asyncio.run(nats_listener())

# Запуск в окремому потоці, щоб Flask міг працювати паралельно
threading.Thread(target=start_nats, daemon=True).start()

@app.route('/get_data')
def get_data():
    return jsonify(guild_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
