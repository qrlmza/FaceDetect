import requests
import json
import time

last_notification_time = 0
notification_interval = 60  # Interval en secondes

def send_discord_notification():
    global last_notification_time
    current_time = time.time()
    if current_time - last_notification_time < notification_interval:
        return
    last_notification_time = current_time
    
    webhook_url = 'url_du_webhook'

    cam_id = "TAPO_C310 - Chambre"

    message = {
        'content': '> ## ⚠️ Un visage a été détecté ! \n> Un visage a été détecté sur la caméra: `' + cam_id + '` !'
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(webhook_url, data=json.dumps(message), headers=headers)

    if response.status_code == 204:
        print('Notification Discord envoyée avec succès !')
    else:
        print(f'Erreur lors de l\'envoi de la notification Discord: {response.status_code}, {response.text}')
