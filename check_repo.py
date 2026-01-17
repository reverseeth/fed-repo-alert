import requests
import os
import json
from pathlib import Path
from datetime import datetime
import pytz

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

URL = "https://markets.newyorkfed.org/api/rp/all/all/results/lastTwoWeeks.json"
STATE_FILE = Path("state.json")

NY_TZ = pytz.timezone("America/New_York")
today_ny = datetime.now(NY_TZ).strftime("%Y-%m-%d")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

r = requests.get(URL, timeout=10)
data = r.json()

repo_ops = data["repo"]["operations"]

# operações SOMENTE do dia atual (NY time)
today_ops = [
    op for op in repo_ops
    if op.get("operationDate") == today_ny
]

total_today = sum(op.get("totalAmtAccepted", 0) for op in today_ops)

previous = 0
if STATE_FILE.exists():
    previous = json.loads(STATE_FILE.read_text()).get("total", 0)

# alerta somente quando sai de 0 hoje
if previous == 0 and total_today > 0:
    send_telegram(
        f"🚨 REPO ATIVO HOJE 🚨\n"
        f"Data: {today_ny}\n"
        f"Total aceito: ${total_today:,}"
    )

STATE_FILE.write_text(json.dumps({"total": total_today}))
