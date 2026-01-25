import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO = "camelbox27-lab/oddsybot"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Futbol Bot Aktif!\n\n"
        "Komutlar:\n"
        "/trigger - Pipeline'ı çalıştır\n"
        "/status - Son çalışma durumu"
    )

async def trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Pipeline tetikleniyor...")
    
    url = f"https://api.github.com/repos/{REPO}/actions/workflows/futbol_bot.yml/dispatches"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"ref": "main"}
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 204:
        await update.message.reply_text("✅ Pipeline başlatıldı! GitHub Actions'da kontrol edin.")
    else:
        await update.message.reply_text(f"❌ Hata: {response.status_code}\n{response.text}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://api.github.com/repos/{REPO}/actions/runs"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        runs = response.json().get("workflow_runs", [])
        if runs:
            last_run = runs[0]
            status = last_run["status"]
            conclusion = last_run.get("conclusion", "running")
            created = last_run["created_at"]
            
            msg = f"📊 Son Çalışma:\n"
            msg += f"Durum: {status}\n"
            msg += f"Sonuç: {conclusion}\n"
            msg += f"Tarih: {created}"
            
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text("❌ Henüz çalışma yok")
    else:
        await update.message.reply_text(f"❌ Hata: {response.status_code}")

def main():
    app = Application.builder().token("8428250321:AAEzuQDkJhHBjPqzgf0FA8kmBaI6hEoIVp4").build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("trigger", trigger))
    app.add_handler(CommandHandler("status", status))
    
    print("🤖 Telegram bot çalışıyor...")
    app.run_polling()

if __name__ == "__main__":
    main()