from flask import Flask, request, jsonify
from services.waha import Waha
from bot.ai_bot import AIbot
import time
import random


app = Flask(__name__)

@app.route('/chatbot/webhook/', methods=['POST'])
def webhook():
    data = request.json
    print(f'EVENTO RECEBIDO: {data}')

    waha = Waha()
    ai_bot = AIbot()

    chat_id = data["payload"]["from"]
    received_message = data["payload"]["body"]


   
    waha.start_typing(chat_id=chat_id)


    response = ai_bot.invoke(question=received_message)

    waha.send_message(
        chat_id=chat_id, 
        message = response,
    )

    waha.stop_typing(chat_id=chat_id)
        
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    #app.run(ssl_context=('path/to/cert.pem', 'path/to/key.pem'))
    app.run(host='0.0.0.0', port=5000, debug=True)	