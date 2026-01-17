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

# --- Fetch data ---
data = requests.get(URL, timeout=10).json()
repo_ops = data["repo"]["operations"]

# --- Filter only today's operations ---
today_ops = [
    op for op in repo_ops
    if op.get("operationDate") == today_ny
]

# --- Aggregate exactly like the site ---
totals = {
    "Treasury": 0,
    "Agency": 0,
    "MBS": 0
}

for op in today_ops:
    sec = op.get("securityType")
    amt = op.get("totalAmtAccepted", 0)
    if sec in totals:
        totals[sec] += amt

total_all = sum(totals.values())

# --- Load previous state ---
previous_total = 0
if STATE_FILE.exists():
    previous_total = json.loads(STATE_FILE.read_text()).get("total", 0)

# --- Alert ONLY when leaving zero ---
if previous_total == 0 and total_all > 0:
    message = (
        f"📅 {today_ny}\n\n"
        f"Repo – Amount ($ Billions)\n"
        f"Treasury: {totals['Treasury'] / 1e9:.3f}\n"
        f"Agency: {totals['Agency'] / 1e9:.3f}\n"
        f"MBS: {totals['MBS'] / 1e9:.3f}\n"
        f"Total: {total_all / 1e9:.3f}"
    )
    send_telegram(message)

# --- Save state ---
STATE_FILE.write_text(json.dumps({"total": total_all}))

# --- TESTE TEMPORÁRIO ---
send_telegram(
    f"TESTE TELEGRAM 🚨\n"
    f"Data: {today_ny}\n"
    f"Treasury: 1.000\n"
    f"Agency: 2.000\n"
    f"MBS: 3.000\n"
    f"Total: 6.000"
)
