import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time
import os
from fractions import Fraction

class SofascoreScraper:
    def __init__(self):
        self.base_url = "https://api.sofascore.com/api/v1"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Origin': 'https://www.sofascore.com',
            'Referer': 'https://www.sofascore.com/'
        }
        
        # ÇEKİLECEK LİGLER artık is_allowed_league fonksiyonunda tanımlı
    
    def is_allowed_league(self, league_name, country_name):
        """Ligin çekilmesine izin verilip verilmediğini kontrol eder - ÜLKE BAZLI"""
        if not league_name:
            return False
        
        league_lower = league_name.lower().strip()
        country_lower = country_name.lower() if country_name else ''
        
        # İzin verilen ülke ve lig kombinasyonları (TAM EŞLEŞME)
        allowed_combinations = {
            'australia': ['a-league men'],
            'austria': ['bundesliga', '2. liga', 'admiral bundesliga'],
            'belgium': ['pro league', 'jupiler pro league', 'challenger pro league'],
            'denmark': ['superliga', 'superligaen', '1. division'],
            'england': ['premier league', 'championship', 'efl championship'],
            'germany': ['bundesliga', '2. bundesliga'],
            'france': ['ligue 1', 'ligue 2'],
            'netherlands': ['eredivisie', 'vriendenloterij eredivisie', 'eerste divisie', 'keuken kampioen divisie'],
            'italy': ['serie a', 'serie b'],
            'spain': ['laliga', 'la liga'],  # LaLiga 2 geçmez artık
            'norway': ['eliteserien'],
            'sweden': ['allsvenskan'],
            'switzerland': ['super league', 'raiffeisen super league', 'challenge league'],
            'turkey': ['süper lig', '1. lig', 'super lig', 'trendyol süper lig'],
            'portugal': ['primeira liga', 'liga portugal', 'liga portugal 2'],
            'scotland': ['premiership', 'scottish premiership', 'championship', 'scottish championship']
        }
        
        # Avrupa kupaları (ülke fark etmez)
        european_cups = [
            'champions league', 'uefa champions league',
            'europa league', 'uefa europa league',
            'conference league', 'uefa conference league'
        ]
        
        # Avrupa kupaları kontrolü
        for cup in european_cups:
            if cup == league_lower or cup in league_lower:
                return True
        
        # Ülke bazlı kontrol
        for country, leagues in allowed_combinations.items():
            if country in country_lower:
                for allowed_league in leagues:
                    # TAM EŞLEŞME
                    if league_lower == allowed_league:
                        return True
                    # İçinde bulunma (ama LaLiga 2, Women vb hariç)
                    if allowed_league in league_lower:
                        # Yasaklılar
                        if any(x in league_lower for x in ['women', 'u23', 'u21', 'reserve', 'fa cup', 'cup']):
                            continue
                        # LaLiga 2 özel durumu
                        if 'laliga 2' in league_lower or 'la liga 2' in league_lower:
                            continue
                        return True
        
        return False
    
    def fractional_to_decimal(self, fractional_str):
        """Fractional oranı (örn: '11/20') desimal orana (2.55) çevirir"""
        try:
            if not fractional_str or fractional_str == 'N/A':
                return None
            
            fraction = Fraction(fractional_str)
            decimal = float(fraction) + 1.0
            return round(decimal, 2)
        except:
            return None
    
    def get_current_date_gmt3(self):
        """GMT+3 saat dilimine göre bugünün tarihini döndürür"""
        tz_gmt3 = pytz.timezone('Europe/Istanbul')
        now = datetime.now(tz_gmt3)
        return now.strftime('%Y-%m-%d')
    
    def get_timezone(self):
        """Kullanılacak saat dilimini döndürür"""
        return pytz.timezone('Europe/Istanbul')
    
    def get_match_details(self, event_id):
        """Maç detaylarını ve GOL BİLGİSİNİ çeker"""
        url = f"{self.base_url}/event/{event_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                event = data.get('event', {})
                
                status_code = event.get('status', {}).get('code')
                status_type = event.get('status', {}).get('type')
                
                is_not_started = status_code in [0, 1] or status_type == 'notstarted'
                
                home_score = event.get('homeScore', {}).get('current')
                away_score = event.get('awayScore', {}).get('current')
                
                return {
                    'is_not_started': is_not_started,
                    'home_score': home_score if not is_not_started else None,
                    'away_score': away_score if not is_not_started else None,
                    'status_code': status_code,
                    'status_type': status_type
                }
            return None
        except Exception as e:
            print(f"  Detay çekme hatası: {e}")
            return None
    
    def get_daily_matches(self, date):
        """Belirli bir tarihteki tüm futbol maçlarını çeker"""
        url = f"{self.base_url}/sport/football/scheduled-events/{date}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                tz_gmt3 = pytz.timezone('Europe/Istanbul')
                now = datetime.now(tz_gmt3)
                
                if 'events' in data:
                    filtered_events = []
                    for event in data['events']:
                        start_timestamp = event.get('startTimestamp')
                        if start_timestamp:
                            match_time = datetime.fromtimestamp(start_timestamp, tz_gmt3)
                            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                            tomorrow_start = today_start + timedelta(days=1)
                            # Sadece bugünün maçları (yarının maçları dahil değil)
                            if today_start <= match_time < tomorrow_start:
                                filtered_events.append(event)
                    data['events'] = filtered_events
                
                return data
            else:
                print(f"Maçlar çekilemedi. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Maç çekme hatası: {e}")
            return None
    
    def get_all_odds_markets(self, event_id, max_retries=3):
        """Belirli bir maç için TÜM bahis marketlerini çeker"""
        endpoints = [
            f"{self.base_url}/event/{event_id}/odds/1/all",
            f"{self.base_url}/event/{event_id}/markets",
        ]
        
        all_markets = []
        
        for endpoint in endpoints:
            for attempt in range(max_retries):
                try:
                    response = requests.get(endpoint, headers=self.headers, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        if 'markets' in data:
                            all_markets.extend(data['markets'])
                        break
                    elif response.status_code == 404:
                        break
                    else:
                        if attempt < max_retries - 1:
                            time.sleep(0.5)
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(0.5)
                    continue
        
        return {'markets': all_markets} if all_markets else None
    
    def parse_all_odds(self, odds_data):
        """Oran verisinden 1X2, Over/Under ve diğer tüm oranları çıkarır - DESİMAL FORMAT"""
        result = {
            'home_win': None,
            'draw': None,
            'away_win': None,
            'over_0_5': None,
            'under_0_5': None,
            'over_1_5': None,
            'under_1_5': None,
            'over_2_5': None,
            'under_2_5': None,
            'over_3_5': None,
            'under_3_5': None,
            'btts_yes': None,
            'btts_no': None
        }
        
        if not odds_data or 'markets' not in odds_data:
            return result
        
        for market in odds_data['markets']:
            market_name = market.get('marketName', '').lower()
            market_id = market.get('marketId')
            
            if market_id == 1 or '1x2' in market_name or 'full time' in market_name:
                choices = market.get('choices', [])
                
                if len(choices) >= 3:
                    if choices[0].get('fractionalValue'):
                        result['home_win'] = self.fractional_to_decimal(choices[0]['fractionalValue'])
                    if choices[1].get('fractionalValue'):
                        result['draw'] = self.fractional_to_decimal(choices[1]['fractionalValue'])
                    if choices[2].get('fractionalValue'):
                        result['away_win'] = self.fractional_to_decimal(choices[2]['fractionalValue'])
            
            if 'over/under' in market_name or 'total' in market_name or 'goals' in market_name:
                for choice in market.get('choices', []):
                    choice_name = choice.get('name', '').lower()
                    fractional = choice.get('fractionalValue')
                    
                    if fractional:
                        decimal = self.fractional_to_decimal(fractional)
                        
                        if '0.5' in choice_name:
                            if 'over' in choice_name:
                                result['over_0_5'] = decimal
                            elif 'under' in choice_name:
                                result['under_0_5'] = decimal
                        
                        if '1.5' in choice_name:
                            if 'over' in choice_name:
                                result['over_1_5'] = decimal
                            elif 'under' in choice_name:
                                result['under_1_5'] = decimal
                        
                        if '2.5' in choice_name:
                            if 'over' in choice_name:
                                result['over_2_5'] = decimal
                            elif 'under' in choice_name:
                                result['under_2_5'] = decimal
                        
                        if '3.5' in choice_name:
                            if 'over' in choice_name:
                                result['over_3_5'] = decimal
                            elif 'under' in choice_name:
                                result['under_3_5'] = decimal
            
            if 'both teams to score' in market_name or 'btts' in market_name:
                for choice in market.get('choices', []):
                    choice_name = choice.get('name', '').lower()
                    fractional = choice.get('fractionalValue')
                    
                    if fractional:
                        decimal = self.fractional_to_decimal(fractional)
                        if 'yes' in choice_name:
                            result['btts_yes'] = decimal
                        elif 'no' in choice_name:
                            result['btts_no'] = decimal
        
        return result
    
    def scrape_matches_with_odds(self, show_debug=True):
        """Bugünün OYNANMAMIŞ maçlarını ve oranlarını çeker - LİG FİLTRELİ"""
        current_date = self.get_current_date_gmt3()
        print(f"Tarih (GMT+3): {current_date}")
        print("Maçlar çekiliyor...")
        
        matches_data = self.get_daily_matches(current_date)
        
        if not matches_data or 'events' not in matches_data:
            print("Maç bulunamadı veya veri çekilemedi.")
            return []
        
        events = matches_data['events']
        print(f"Toplam {len(events)} maç bulundu.")
        
        all_matches = []
        skipped_no_odds = 0
        skipped_already_started = 0
        skipped_league = 0
        
        for idx, event in enumerate(events, 1):
            try:
                event_id = event.get('id')
                home_team = event.get('homeTeam', {}).get('name', 'N/A')
                away_team = event.get('awayTeam', {}).get('name', 'N/A')
                tournament = event.get('tournament', {}).get('name', 'N/A')
                category = event.get('tournament', {}).get('category', {}).get('name', 'N/A')
                
                # 🔥 LİG FİLTRESİ (ÜLKE BAZLI)
                if not self.is_allowed_league(tournament, category):
                    if idx <= 50:  # İlk 50 maç için debug
                        print(f"{idx}/{len(events)} - {home_team} vs {away_team} ({category} - {tournament})")
                        print(f"   ⛔ Atlandı - Lig/Ülke listede yok")
                    skipped_league += 1
                    continue
                
                start_timestamp = event.get('startTimestamp')
                if start_timestamp:
                    tz_gmt3 = pytz.timezone('Europe/Istanbul')
                    match_time = datetime.fromtimestamp(start_timestamp, tz_gmt3)
                    match_time_str = match_time.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    match_time_str = 'N/A'
                
                print(f"{idx}/{len(events)} - {home_team} vs {away_team} ({tournament}) - Kontrol ediliyor...")
                
                match_details = self.get_match_details(event_id)
                
                if match_details and not match_details['is_not_started']:
                    if idx <= 50:  # Debug için
                        print(f"   ⛔ Atlandı - Maç başlamış/bitti")
                    skipped_already_started += 1
                    time.sleep(0.3)
                    continue
                
                odds_data = self.get_all_odds_markets(event_id)
                
                if show_debug and idx <= 2 and odds_data:
                    print("\n" + "="*60)
                    print(f"DEBUG - HAM ORAN VERİSİ (Maç #{idx}):")
                    print(f"Toplam Market Sayısı: {len(odds_data.get('markets', []))}")
                    for market in odds_data.get('markets', [])[:5]:
                        print(f"  - {market.get('marketName')} (ID: {market.get('marketId')})")
                    print("="*60 + "\n")
                
                odds = self.parse_all_odds(odds_data)
                
                has_1x2 = odds['home_win'] and odds['draw'] and odds['away_win']
                
                if not has_1x2:
                    print(f"   ⚠️  Atlandı - 1X2 oranları bulunamadı")
                    skipped_no_odds += 1
                    time.sleep(0.3)
                    continue
                
                match_info = {
                    'event_id': event_id,
                    'date_time': match_time_str,
                    'country': category,
                    'league': tournament,
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_win': odds['home_win'],
                    'draw': odds['draw'],
                    'away_win': odds['away_win'],
                    'over_2_5': odds['over_2_5'],
                    'under_2_5': odds['under_2_5'],
                    'over_0_5': odds['over_0_5'],
                    'under_0_5': odds['under_0_5'],
                    'over_1_5': odds['over_1_5'],
                    'under_1_5': odds['under_1_5'],
                    'over_3_5': odds['over_3_5'],
                    'under_3_5': odds['under_3_5'],
                    'btts_yes': odds['btts_yes'],
                    'btts_no': odds['btts_no']
                }
                
                all_matches.append(match_info)
                
                over_2_5_str = f"O2.5:{odds['over_2_5']}" if odds['over_2_5'] else "O2.5:-"
                under_2_5_str = f"U2.5:{odds['under_2_5']}" if odds['under_2_5'] else "U2.5:-"
                print(f"   ✅ Kaydedildi - 1:{odds['home_win']} X:{odds['draw']} 2:{odds['away_win']} | {over_2_5_str} {under_2_5_str}")
                
                time.sleep(0.7)
                
            except Exception as e:
                print(f"Hata (Event ID: {event.get('id')}): {e}")
                continue
        
        print(f"\n📊 Özet:")
        print(f"   Toplam maç: {len(events)}")
        print(f"   Lig filtresinden elendi: {skipped_league}")
        print(f"   Başlamış/bitti: {skipped_already_started}")
        print(f"   Oransız: {skipped_no_odds}")
        print(f"   ✅ İzin verilen liglerden + Oynanmamış + Oranlı: {len(all_matches)}")
        
        return all_matches
    
    def save_to_json(self, data, filename='sofascore_matches.json'):
        """Veriyi JSON formatında kaydeder"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ JSON dosyası kaydedildi: {filename}")
    
    def save_to_excel(self, data, filename='sofascore_matches.xlsx'):
        """Veriyi Excel formatında kaydeder - ONDALIK SAYILARI KORUR"""
        df = pd.DataFrame(data)
        
        column_order = [
            'event_id', 'date_time', 'country', 'league', 
            'home_team', 'away_team',
            'home_win', 'draw', 'away_win',
            'over_2_5', 'under_2_5',
            'over_0_5', 'under_0_5',
            'over_1_5', 'under_1_5',
            'over_3_5', 'under_3_5',
            'btts_yes', 'btts_no'
        ]
        
        df = df[column_order]
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Maçlar')
            
            workbook = writer.book
            worksheet = writer.sheets['Maçlar']
            
            from openpyxl.styles import numbers
            
            odds_columns = ['G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R']
            
            for col in odds_columns:
                for row in range(2, len(df) + 2):
                    cell = worksheet[f'{col}{row}']
                    cell.number_format = '0.00'
        
        print(f"✓ Excel dosyası kaydedildi: {filename} (ondalık sayılar korundu)")
    
    def run(self, show_debug=True):
        """Ana çalıştırma fonksiyonu"""
        print("=" * 60)
        print("SOFASCORE MAÇ VE ORAN ÇEKİCİ (LİG FİLTRELİ)")
        print("=" * 60)
        
        matches = self.scrape_matches_with_odds(show_debug=show_debug)
        
        if not matches:
            print("\n! Kaydedilecek veri bulunamadı.")
            return
        
        print(f"\n✓ Toplam {len(matches)} OYNANMAMIŞ maç verisi çekildi.")
        print("\nDosyalar kaydediliyor...")
        
        current_date = self.get_current_date_gmt3()
        json_filename = f'sofascore_matches_{current_date}.json'
        excel_filename = f'sofascore_matches_{current_date}.xlsx'
        
        self.save_to_json(matches, json_filename)
        self.save_to_excel(matches, excel_filename)
        
        print("\n" + "=" * 60)
        print("İŞLEM TAMAMLANDI!")
        print("=" * 60)

if __name__ == "__main__":
    try:
        import openpyxl
    except ImportError:
        print("UYARI: openpyxl kütüphanesi bulunamadı.")
        print("Lütfen şu komutu çalıştırın: pip install openpyxl")
        exit(1)
    
    scraper = SofascoreScraper()
    scraper.run(show_debug=True)