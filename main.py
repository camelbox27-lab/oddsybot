import os

# Klasörleri oluştur
os.makedirs('filtered', exist_ok=True)
os.makedirs('merged_json', exist_ok=True)
os.makedirs('docs', exist_ok=True)
import subprocess
import os

print("🤖 Bot sistemi başlatılıyor...")

# 1. SOFA BOT
os.chdir('sofa')
subprocess.run(['python', 'bet365data.py'])

# 2. EXCEL TO JSON
os.chdir('../mackolik-excel-json')
subprocess.run(['python', 'excel_to_json_bot.py'])

# 3. MERGER
os.chdir('../merged')
subprocess.run(['python', 'match_merger_bot.py'])

# 4. FILTER
os.chdir('../filtered')
subprocess.run(['python', 'filter_bot.py'])

print("✅ Tüm botlar çalıştı!")