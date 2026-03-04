import asyncio
import json
import threading
from flask import Flask, jsonify
from nats.aio.client import Client as NATS

app = Flask(__name__)
guild_data = {"last_update": "waiting", "members": []}

async def nats_listener():
    nc = NATS()
    await nc.connect("nats://public:thenewalbiondata@nats.albion-online-data.com:34222")
    
    # Підписуємось на топік з даними
    async def message_handler(msg):
        data = json.loads(msg.data.decode())
        # Тут треба додати фільтр за ID твоєї гільдії, 
        # коли знайдеш правильний топік у документації NATS
        if "GuildId" in data and data["GuildId"] == "wa7AF_VWSqiUxQBRI-VAXw":
            guild_data["members"] = data
            guild_data["last_update"] = "OK"

    await nc.subscribe("albion.events.guild", cb=message_handler)
    
    # Тримаємо з'єднання відкритим
    await asyncio.Future() 

def start_nats():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(nats_listener())

# Запускаємо NATS у фоновому потоці
threading.Thread(target=start_nats, daemon=True).start()

@app.route('/get_data')
def get_data():
    return jsonify(guild_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)