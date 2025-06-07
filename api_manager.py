import requests
import json

url = "https://marco-moser.app.n8n.cloud/webhook/564e0777-6096-4cee-a563-1db37f1ce4d8"


def upload(articolo, alimento, quantità, time, referente):

    payload = json.dumps(
        {
            "articolo": articolo,
            "alimento": alimento,
            "quantità": quantità,
            "time": time,
            "referente": referente,
        }
    )
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    return response.text
