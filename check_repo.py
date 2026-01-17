import requests
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

URL = "https://markets.newyorkfed.org/api/rp/all/all/results/lastTwoWeeks.json"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

r = requests.get(URL, timeout=10)
data = r.json()

repo_ops = data["repo"]["operations"]

total = sum(op["totalAmtAccepted"] for op in repo_ops)

if total > 0:
    send_telegram(f"🚨 REPO ATIVO 🚨\nTotal aceito: {total:,}")
