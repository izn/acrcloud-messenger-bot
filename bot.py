import json
import os
import audio
import dotenv
from flask import Flask, request
from messenger import MessengerClient
from messenger.content_types import TextMessage

dotenv.load_dotenv(dotenv.find_dotenv(), override=True)

FACEBOOK_VERIFICATION_TOKEN = os.environ.get('FACEBOOK_VERIFICATION_TOKEN')
FACEBOOK_PAGE_ACCESS_TOKEN = os.environ.get('FACEBOOK_PAGE_ACCESS_TOKEN')

app = Flask(__name__)
client = MessengerClient(FACEBOOK_PAGE_ACCESS_TOKEN)

@app.route('/', methods=['GET'])
def handle_verification():
  if request.args.get('hub.verify_token', '') == FACEBOOK_VERIFICATION_TOKEN:
    return request.args.get('hub.challenge', '')

  return 'Invalid verification token'

@app.route('/', methods=['POST'])
def handle_messages():
  message_entries = json.loads(request.data.decode('utf8'))['entry']

  for entry in message_entries:
    for message_data in entry['messaging']:
        sender_id = message_data['sender']['id']
        message = message_data["message"]

        if ("attachments" in message):
            for attachment in message["attachments"]:
                if (attachment["type"] == 'audio'):
                    client.send(sender_id, TextMessage('Estou ouvindo seu áudio! Um segundo, por favor :)'))

                    audio_info = audio.recognize(attachment["payload"]["url"])

                    if (audio_info['status']['code'] == 1001):
                        client.send(sender_id, TextMessage('Infelizmente não consegui reconhecer. :/'))
                        client.send(sender_id, TextMessage('Tente gravar novamente mais perto ou por mais tempo.'))
                    else:
                        artist = audio_info['metadata']['music'][0]['artists'][0]['name']
                        song = audio_info['metadata']['music'][0]['title']

                        client.send(sender_id, TextMessage('Detectei a seguinte música: %s - %s' % (artist, song)))
        elif ("text" in message):
            client.send(sender_id, TextMessage('Oi! Grava um áudio aí pra nóis.'))
        else:
            client.send(sender_id, TextMessage('Não entendi :('))
            client.send(sender_id, TextMessage('Mande uma gravação de alguma música que vou tentar identificar qual é.'))

  return 'OK'

if __name__ == '__main__':
  app.run(debug=True)
