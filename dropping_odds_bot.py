import requests
import json
from datetime import datetime
import pytz

class DroppingOddsBot:
    def __init__(self):
        self.base_url = "https://api.sofascore.com/api/v1"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
    
    def get_dropping_odds_matches(self):
        url = f"{self.base_url}/odds/1/dropping/football"
        
        print(f"🔍 Oran düşen maçlar çekiliyor...\n")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ HTTP Hata: {response.status_code}")
                return []
            
            data = response.json()
            events = data.get('events', [])
            odds_map = data.get('oddsMap', {})
            
            if not events:
                print("❌ Veri bulunamadı")
                return []
            
            print(f"📊 {len(events)} oran düşen maç bulundu\n")
            
            dropping_matches = []
            tz_gmt3 = pytz.timezone('Europe/Istanbul')
            
            for idx, event in enumerate(events, 1):
                try:
                    event_id = str(event.get('id'))
                    home_team = event.get('homeTeam', {}).get('name', 'N/A')
                    away_team = event.get('awayTeam', {}).get('name', 'N/A')
                    tournament = event.get('tournament', {}).get('name', 'N/A')
                    category = event.get('tournament', {}).get('category', {}).get('name', 'N/A')
                    
                    # ORAN VERİSİ
                    odds_data = odds_map.get(event_id, {})
                    drop_percentage = odds_data.get('percentage', 0)
                    choice_name = odds_data.get('choiceName', '')
                    
                    # ORANLAR
                    odds_info = odds_data.get('odds', {})
                    choices = odds_info.get('choices', [])
                    
                    current_odds = {}
                    initial_odds = {}
                    
                    for choice in choices:
                        name = choice.get('name')
                        current_frac = choice.get('fractionalValue', '0/1')
                        initial_frac = choice.get('initialFractionalValue', '0/1')
                        
                        # Kesirli oranı ondalığa çevir
                        try:
                            num, den = current_frac.split('/')
                            current_decimal = round(float(num) / float(den) + 1, 2)
                        except:
                            current_decimal = 0
                        
                        try:
                            num, den = initial_frac.split('/')
                            initial_decimal = round(float(num) / float(den) + 1, 2)
                        except:
                            initial_decimal = 0
                        
                        current_odds[name] = current_decimal
                        initial_odds[name] = initial_decimal
                    
                    start_timestamp = event.get('startTimestamp')
                    if start_timestamp:
                        match_time = datetime.fromtimestamp(start_timestamp, tz_gmt3)
                        saat = match_time.strftime('%H:%M')
                    else:
                        saat = 'N/A'
                    
                    match = {
                        'categoryKey': 'oran-dusen-maclar',
                        'homeTeam': home_team,
                        'awayTeam': away_team,
                        'saat': saat,
                        'tournament': tournament,
                        'category': category,
                        'dropPercentage': drop_percentage,
                        'droppingChoice': choice_name,
                        'currentOdds': current_odds,
                        'initialOdds': initial_odds,
                    }
                    
                    dropping_matches.append(match)
                    
                    print(f"[{idx}] {home_team} vs {away_team}")
                    print(f"    Düşüş: %{drop_percentage:.1f} ({choice_name})")
                    print(f"    İlk: {initial_odds}")
                    print(f"    Şuan: {current_odds}")
                    print(f"    Saat: {saat}\n")
                    
                except Exception as e:
                    print(f"   ❌ Hata: {e}")
                    continue
            
            return dropping_matches
            
        except Exception as e:
            print(f"❌ Hata: {e}")
            return []
    
    def save_to_json(self, matches):
        if not matches:
            print("⚠️ Kaydedilecek maç yok")
            return
        
        output_file = 'filtered/oran_dusen_maclar.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(matches, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ {len(matches)} maç kaydedildi!")
    
    def run(self):
        print(f"🔍 ORAN DÜŞEN MAÇLAR")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
        
        matches = self.get_dropping_odds_matches()
        
        if matches:
            self.save_to_json(matches)
        else:
            print("\n⚠️ Maç bulunamadı")
        
        print("\n✅ TAMAMLANDI!")

if __name__ == "__main__":
    bot = DroppingOddsBot()
    bot.run()