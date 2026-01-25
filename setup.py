import os
import json
import subprocess
import sys

# ========================
# KONFIGÜRASYON
# ========================
GITHUB_REPO = "camelbox27-lab/bot"  # Repo adınızı buraya yazın
TELEGRAM_BOT_TOKEN = "8428250321:AAEzuQDkJhHBjPqzgf0FA8kmBaI6hEoIVp4"
GITHUB_TOKEN = input("GitHub Personal Access Token girin: ").strip()

# ========================
# RENKLER
# ========================
class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg): print(f"{Color.GREEN}✅ {msg}{Color.END}")
def print_error(msg): print(f"{Color.RED}❌ {msg}{Color.END}")
def print_info(msg): print(f"{Color.BLUE}ℹ️  {msg}{Color.END}")
def print_warning(msg): print(f"{Color.YELLOW}⚠️  {msg}{Color.END}")

# ========================
# 1. GITHUB ACTIONS DOSYASI
# ========================
def create_github_actions():
    print_info("GitHub Actions dosyası oluşturuluyor...")
    
    workflow_dir = ".github/workflows"
    os.makedirs(workflow_dir, exist_ok=True)
    
    workflow_content = """name: Futbol Pipeline

on:
  schedule:
    - cron: '0 6 0 * *'  # Her gün 09:00 (UTC+3)
  workflow_dispatch:  # Manuel tetikleme

jobs:
  run-pipeline:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Create Firebase key file
        run: |
          echo '${{ secrets.FIREBASE_KEY }}' > serviceAccountKey.json
      
      - name: Run main pipeline
        run: python main.py
      
      - name: Run istatistik pipeline
        run: python istatistik/main.py
      
      - name: Cleanup
        run: rm -f serviceAccountKey.json
"""
    
    with open(f"{workflow_dir}/futbol_bot.yml", "w", encoding="utf-8") as f:
        f.write(workflow_content)
    
    print_success("GitHub Actions dosyası oluşturuldu!")

# ========================
# 2. TELEGRAM BOT
# ========================
def create_telegram_bot():
    print_info("Telegram bot dosyası oluşturuluyor...")
    
    bot_content = f"""import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

GITHUB_TOKEN = "{GITHUB_TOKEN}"
REPO = "{GITHUB_REPO}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Futbol Bot Aktif!\\n\\n"
        "Komutlar:\\n"
        "/trigger - Pipeline'ı çalıştır\\n"
        "/status - Son çalışma durumu"
    )

async def trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Pipeline tetikleniyor...")
    
    url = f"https://api.github.com/repos/{{REPO}}/actions/workflows/futbol_bot.yml/dispatches"
    headers = {{
        "Authorization": f"token {{GITHUB_TOKEN}}",
        "Accept": "application/vnd.github.v3+json"
    }}
    data = {{"ref": "main"}}
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 204:
        await update.message.reply_text("✅ Pipeline başlatıldı! GitHub Actions'da kontrol edin.")
    else:
        await update.message.reply_text(f"❌ Hata: {{response.status_code}}\\n{{response.text}}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://api.github.com/repos/{{REPO}}/actions/runs"
    headers = {{
        "Authorization": f"token {{GITHUB_TOKEN}}",
        "Accept": "application/vnd.github.v3+json"
    }}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        runs = response.json().get("workflow_runs", [])
        if runs:
            last_run = runs[0]
            status = last_run["status"]
            conclusion = last_run.get("conclusion", "running")
            created = last_run["created_at"]
            
            msg = f"📊 Son Çalışma:\\n"
            msg += f"Durum: {{status}}\\n"
            msg += f"Sonuç: {{conclusion}}\\n"
            msg += f"Tarih: {{created}}"
            
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text("❌ Henüz çalışma yok")
    else:
        await update.message.reply_text(f"❌ Hata: {{response.status_code}}")

def main():
    app = Application.builder().token("{TELEGRAM_BOT_TOKEN}").build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("trigger", trigger))
    app.add_handler(CommandHandler("status", status))
    
    print("🤖 Telegram bot çalışıyor...")
    app.run_polling()

if __name__ == "__main__":
    main()
"""
    
    with open("telegram_trigger.py", "w", encoding="utf-8") as f:
        f.write(bot_content)
    
    print_success("Telegram bot dosyası oluşturuldu!")

# ========================
# 3. REQUIREMENTS GÜNCELLE
# ========================
def update_requirements():
    print_info("requirements.txt güncelleniyor...")
    
    new_deps = [
        "python-telegram-bot==20.7",
        "requests"
    ]
    
    try:
        with open("requirements.txt", "r") as f:
            existing = f.read().splitlines()
    except:
        existing = []
    
    for dep in new_deps:
        if dep.split("==")[0] not in " ".join(existing):
            existing.append(dep)
    
    with open("requirements.txt", "w") as f:
        f.write("\n".join(existing))
    
    print_success("requirements.txt güncellendi!")

# ========================
# 4. FIREBASE SECRET EKLE
# ========================
def add_firebase_secret():
    print_info("Firebase key GitHub Secrets'a ekleniyor...")
    
    try:
        with open("serviceAccountKey.json", "r") as f:
            firebase_key = f.read()
    except:
        print_error("serviceAccountKey.json bulunamadı! Manuel eklemeniz gerekecek.")
        return
    
    print_warning("Firebase key'i manuel eklemeniz gerekiyor:")
    print_info(f"1. https://github.com/{GITHUB_REPO}/settings/secrets/actions adresine gidin")
    print_info("2. 'New repository secret' tıklayın")
    print_info("3. Name: FIREBASE_KEY")
    print_info("4. Value: serviceAccountKey.json dosyasının içeriği")
    print_info("5. 'Add secret' tıklayın")

# ========================
# 5. GIT PUSH
# ========================
def git_push():
    print_info("Değişiklikler GitHub'a gönderiliyor...")
    
    commands = [
        "git add .",
        'git commit -m "🤖 Otomatik kurulum: GitHub Actions + Telegram Bot"',
        "git push origin main"
    ]
    
    for cmd in commands:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print_error(f"Git komutu başarısız: {cmd}")
            print_error(result.stderr)
            return False
    
    print_success("GitHub'a gönderildi!")
    return True

# ========================
# 6. PAKET KURULUMU
# ========================
def install_packages():
    print_info("Python paketleri kuruluyor...")
    
    result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print_success("Paketler kuruldu!")
    else:
        print_error("Paket kurulumu başarısız!")
        print_error(result.stderr)

# ========================
# ANA KURULUM
# ========================
def main():
    print(f"\n{Color.BLUE}{'='*50}")
    print("🚀 FUTBOL BOT OTOMATİK KURULUM")
    print(f"{'='*50}{Color.END}\n")
    
    print_info(f"Repo: {GITHUB_REPO}")
    print_info(f"Telegram Bot: @Aus_git_bot")
    print_info(f"Klasör: {os.getcwd()}\n")
    
    # Kurulum adımları
    create_github_actions()
    create_telegram_bot()
    update_requirements()
    install_packages()
    add_firebase_secret()
    
    print(f"\n{Color.GREEN}{'='*50}")
    print("✅ KURULUM TAMAMLANDI!")
    print(f"{'='*50}{Color.END}\n")
    
    print_info("SONRAKİ ADIMLAR:")
    print("1. Firebase key'i GitHub Secrets'a ekleyin (yukarıdaki talimatları izleyin)")
    print("2. Git push yapın: git add . && git commit -m 'Setup' && git push")
    print("3. Telegram bot'u çalıştırın: python telegram_trigger.py")
    print("\n📱 Telegram'dan /trigger komutuyla pipeline'ı tetikleyebilirsiniz!")
    print("⏰ GitHub Actions her gün 09:00'da otomatik çalışacak!\n")

if __name__ == "__main__":
    main()