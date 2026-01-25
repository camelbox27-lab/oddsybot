from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
from datetime import datetime
import re

def scrape_league_cards(driver, wait, country, league_name, is_turkey=False):
    """Belirli bir lig için kart verilerini çeker"""
    print(f"\n{'='*60}")
    print(f"🟨 {country} - {league_name} KART VERİSİ İŞLENİYOR...")
    print(f"{'='*60}")
    
    max_retries = 3 if not is_turkey else 5  # Türkiye için daha fazla deneme
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Ana sayfaya dön
            if retry_count > 0:
                print("🔄 Ana sayfaya dönülüyor...")
                driver.get('https://www.adamchoi.co.uk/cards/detailed')
                time.sleep(4)
            
            # Ülke seç
            print(f"🌍 Ülke seçiliyor: {country} (Deneme {retry_count + 1}/{max_retries})")
            time.sleep(3)
            
            country_select = Select(wait.until(EC.presence_of_element_located((By.ID, 'country'))))
            
            if is_turkey:
                print("   🇹🇷 Türkiye özel işlemi başlatılıyor...")
                # Türkiye için tüm seçenekleri yazdır
                print("   Mevcut ülkeler:")
                for opt in country_select.options:
                    if 'turkey' in opt.text.lower():
                        print(f"      ✓ BULUNDU: '{opt.text}'")
            
            # Ülke seç
            country_found = False
            for option in country_select.options:
                option_text = option.text.strip()
                if country.lower() == option_text.lower() or country.lower() in option_text.lower():
                    print(f"   ✓ Ülke bulundu: '{option_text}'")
                    country_select.select_by_visible_text(option_text)
                    country_found = True
                    break
            
            if not country_found:
                print(f"   ⚠️ '{country}' tam eşleşmedi, direkt seçiliyor...")
                country_select.select_by_visible_text(country)
            
            wait_time = 5 if is_turkey else 3
            print(f"   ⏳ {wait_time} saniye bekleniyor...")
            time.sleep(wait_time)
            
            # Lig seç
            print(f"⚽ Lig seçiliyor: {league_name}")
            league_select = Select(wait.until(EC.presence_of_element_located((By.ID, 'league'))))
            
            if is_turkey:
                # Türkiye için tüm ligleri yazdır
                print("   Mevcut ligler:")
                for opt in league_select.options:
                    opt_text = opt.text.strip()
                    if opt_text:
                        print(f"      - '{opt_text}'")
                        if 'turkish' in opt_text.lower() or 'super' in opt_text.lower() or 'lig' in opt_text.lower():
                            print(f"      ✓ EŞLEŞME: '{opt_text}'")
            
            # Lig ismini esnek şekilde bul
            league_found = False
            for option in league_select.options:
                option_text = option.text.strip()
                if not option_text:
                    continue
                
                # Türkiye için özel kontrol
                if is_turkey:
                    if ('turkish' in option_text.lower() and 'super' in option_text.lower()) or \
                       ('turkish' in option_text.lower() and 'lig' in option_text.lower()) or \
                       'süper lig' in option_text.lower():
                        print(f"   ✓✓✓ TÜRKİYE LİGİ BULUNDU: '{option_text}'")
                        league_select.select_by_visible_text(option_text)
                        league_found = True
                        break
                else:
                    # Diğer ligler için
                    if league_name.lower() in option_text.lower():
                        print(f"   ✓ Eşleşen lig bulundu: '{option_text}'")
                        league_select.select_by_visible_text(option_text)
                        league_found = True
                        break
            
            if not league_found:
                print(f"   ⚠️ Lig bulunamadı, tam isimle deneniyor: '{league_name}'")
                league_select.select_by_visible_text(league_name)
            
            wait_time = 8 if is_turkey else 6
            print(f"⏳ Veriler yükleniyor ({wait_time} saniye)...")
            time.sleep(wait_time)
            
            # Tabloyu kontrol et
            rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            print(f"📊 {len(rows)} satır bulundu.")

            if len(rows) == 0:
                print(f"⚠️ Veri bulunamadı, tekrar deneniyor...")
                retry_count += 1
                continue

            raw_data = []
            seen_matches = set()
            
            for idx, row in enumerate(rows):
                try:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    
                    if len(cols) == 5:
                        tarih_idx, ev_idx, skor_idx, dep_idx = 0, 1, 2, 3
                    elif len(cols) >= 6:
                        tarih_idx, ev_idx, skor_idx, dep_idx = 0, 2, 3, 4
                    else:
                        continue
                    
                    tarih = cols[tarih_idx].text.strip()
                    ev = cols[ev_idx].text.strip()
                    skor = cols[skor_idx].text.strip()
                    dep = cols[dep_idx].text.strip()
                    
                    if not tarih or not ev or not dep or not skor:
                        continue
                    
                    ev_kart = ""
                    dep_kart = ""
                    if " - " in skor:
                        parts = skor.split(" - ")
                        if len(parts) == 2:
                            ev_kart = parts[0].strip()
                            dep_kart = parts[1].strip()
                    elif "-" in skor:
                        parts = skor.split("-")
                        if len(parts) == 2:
                            ev_kart = parts[0].strip()
                            dep_kart = parts[1].strip()
                    
                    if ev_kart and dep_kart:
                        match_key = f"{tarih}_{ev}_{dep}_{ev_kart}_{dep_kart}"
                        if match_key not in seen_matches:
                            seen_matches.add(match_key)
                            raw_data.append({
                                'Tarih': tarih,
                                'Ev Sahibi': ev,
                                'Ev Kart': ev_kart,
                                'Deplasman': dep,
                                'Dep Kart': dep_kart
                            })
                            
                            # İlk 3 maçı göster
                            if idx < 3:
                                print(f"  ✓ Maç {idx+1}: {ev} vs {dep} -> {ev_kart}-{dep_kart}")
                except:
                    continue

            if not raw_data:
                print(f"❌ {league_name} için veri bulunamadı!")
                retry_count += 1
                time.sleep(3)
                continue

            df = pd.DataFrame(raw_data)
            print(f"✅ Toplam {len(df)} benzersiz maç bulundu.")
            
            return df
            
        except Exception as e:
            print(f"❌ Deneme {retry_count + 1} başarısız: {e}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"🔄 {max_retries - retry_count} deneme hakkı kaldı...")
                time.sleep(5)
            else:
                print(f"❌ {country} - {league_name} için tüm denemeler başarısız!")
                import traceback
                traceback.print_exc()
                return None
    
    return None


def create_card_excel(df, country, league_name):
    """Kart verisinden Excel dosyası oluşturur"""
    
    all_teams = sorted(set(df['Ev Sahibi'].unique()) | set(df['Deplasman'].unique()))
    
    # Dosya adı oluştur
    safe_name = re.sub(r'[\\/*?:\[\]]', '', f"{country}_{league_name}").replace(' ', '_')
    file_name = f"KART_DATA_{safe_name}_{datetime.now().strftime('%d%m_%H%M')}.xlsx"
    
    print(f"\n💾 Excel dosyası oluşturuluyor: {file_name}")
    print(f"📋 {len(all_teams)} takım bulundu")
    
    with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
        # Tüm maçlar sayfası
        df_all = df.copy()
        df_all['Kart'] = df_all['Ev Kart'] + ' - ' + df_all['Dep Kart']
        df_all_sorted = df_all.sort_values('Tarih', ascending=False)
        df_all_sorted[['Tarih', 'Ev Sahibi', 'Kart', 'Deplasman']].to_excel(
            writer, sheet_name='Tüm Maçlar', index=False
        )
        
        # Her takım için ayrı sayfa
        for team in all_teams:
            if not team or len(team.strip()) == 0:
                continue
            
            team_matches = []
            
            # İç saha maçları
            home = df[df['Ev Sahibi'] == team].copy()
            for _, match in home.iterrows():
                team_matches.append({
                    'Tarih': match['Tarih'],
                    'Rakip': match['Deplasman'],
                    'Kart': f"{match['Ev Kart']} - {match['Dep Kart']}"
                })
            
            # Dış saha maçları
            away = df[df['Deplasman'] == team].copy()
            for _, match in away.iterrows():
                team_matches.append({
                    'Tarih': match['Tarih'],
                    'Rakip': match['Ev Sahibi'],
                    'Kart': f"{match['Dep Kart']} - {match['Ev Kart']}"
                })
            
            # Tarihe göre sırala
            team_df = pd.DataFrame(team_matches)
            team_df = team_df.sort_values('Tarih', ascending=False).reset_index(drop=True)
            
            # Excel sekme ismi temizleme
            clean_name = re.sub(r'[\\/*?:\[\]]', '', team)[:30].strip()
            if not clean_name:
                clean_name = "Team_Data"

            team_df.to_excel(writer, sheet_name=clean_name, index=False)
        
        print(f"  ✓ {len(all_teams)} takım için veriler kaydedildi")
    
    print(f"✨ {country} - {league_name} tamamlandı: {file_name}")
    return file_name


def scrape_all_cards():
    """Tüm ligler için kart verilerini çeker"""
    
    # Ligler listesi (Ülke, Lig Adı, Türkiye mi?)
    leagues = [
        ('England', 'Premier League', False),
        ('Germany', 'Bundesliga', False),
        ('Italy', 'Serie A', False),
        ('France', 'Ligue 1', False),
        ('Spain', 'La Liga', False),
        ('Turkey', 'Turkish Super League', True),  # Türkiye bayrağı!
        ('Netherlands', 'Eredivisie', False),
        ('Portugal', 'Portugese Liga NOS', False)
    ]
    
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    # Cloud/Server settings
    chrome_options.add_argument('--headless=new') 
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 25)
    
    created_files = []
    failed_leagues = []
    
    try:
        print("🌐 KART VERİSİ SAYFASINA GİDİLİYOR...")
        driver.get('https://www.adamchoi.co.uk/cards/detailed')
        time.sleep(4)
        
        for country, league, is_turkey in leagues:
            df = scrape_league_cards(driver, wait, country, league, is_turkey)
            
            if df is not None and len(df) > 0:
                file_name = create_card_excel(df, country, league)
                created_files.append(file_name)
                
                if is_turkey:
                    print("\n" + "🇹🇷"*20)
                    print("TÜRKİYE BAŞARIYLA TAMAMLANDI!")
                    print("🇹🇷"*20 + "\n")
            else:
                print(f"⚠️ {country} - {league} atlandı (veri yok)")
                failed_leagues.append(f"{country} - {league}")
            
            time.sleep(4)  # Ligler arası daha uzun bekleme
        
        print(f"\n{'='*60}")
        print("🎉 TÜM LİGLER KART VERİSİ TAMAMLANDI!")
        print(f"{'='*60}")
        print(f"\n📊 Oluşturulan Dosyalar ({len(created_files)}):")
        for i, file in enumerate(created_files, 1):
            emoji = "🇹🇷" if "Turkey" in file else "⚽"
            print(f"  {emoji} {i}. {file}")
        
        if failed_leagues:
            print(f"\n⚠️ Başarısız Ligler ({len(failed_leagues)}):")
            for i, league in enumerate(failed_leagues, 1):
                print(f"  {i}. {league}")
        else:
            print(f"\n✨✨✨ TAMAMI BAŞARILI - HİÇ HATA YOK! ✨✨✨")
        
    except Exception as e:
        print(f"\n❌ GENEL HATA: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🔒 Tarayıcı kapatılıyor...")
        driver.quit()
        print("✅ İşlem tamamlandı!")


if __name__ == "__main__":
    scrape_all_cards()