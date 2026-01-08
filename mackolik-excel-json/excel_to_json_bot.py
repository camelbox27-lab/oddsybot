import pandas as pd
import json
from datetime import datetime
import os
import glob

class ExcelToJsonConverter:
    def __init__(self, excel_folder=".", output_folder="json_output"):
        self.excel_folder = excel_folder
        self.output_folder = output_folder
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            print(f"📁 '{output_folder}' klasörü oluşturuldu")
    
    def clean_team_name(self, name):
        if pd.isna(name):
            return ""
        return str(name).strip()
    
    def clean_odd(self, value):
        if pd.isna(value) or value == '' or value == 0:
            return None
        try:
            if isinstance(value, str):
                value = value.replace(',', '.')
            return float(value)
        except:
            return None
    
    def parse_sheet(self, df, sheet_name=""):
        try:
            print(f"📊 '{sheet_name}' - Toplam {len(df)} satır bulundu")
            
            matches = []
            
            for index, row in df.iterrows():
                try:
                    home_team = self.clean_team_name(row.get('Home', row.get('Ev Sahibi', '')))
                    away_team = self.clean_team_name(row.get('Away', row.get('Misafir', '')))
                    
                    if not home_team or not away_team:
                        continue
                    
                    match_data = {
                        'home_team': home_team,
                        'away_team': away_team,
                        'saat': str(row.get('Saat', '')),
                        'lig': str(row.get('Lig', '')),
                        
                        'ms_1': self.clean_odd(row.get('1')),
                        'ms_x': self.clean_odd(row.get('0', row.get('X'))),
                        'ms_2': self.clean_odd(row.get('2')),
                        
                        'kg_var': self.clean_odd(row.get('Karsılıklı Gol', row.get('Var'))),
                        'kg_yok': self.clean_odd(row.get('Yok')),
                        
                        'ust_2_5': self.clean_odd(row.get('2.5 üst', row.get('2.5U'))),
                        'alt_2_5': self.clean_odd(row.get('2.5 alt', row.get('2.5A'))),
                        
                        'ust_3_5': self.clean_odd(row.get('3.5 üst', row.get('3.5U'))),
                        'alt_3_5': self.clean_odd(row.get('3.5 alt', row.get('3.5A'))),
                        
                        'ust_5_5': self.clean_odd(row.get('5.5üst', row.get('5.5U'))),
                        'alt_5_5': self.clean_odd(row.get('5.5alt', row.get('5.5A'))),
                        
                        '1x': self.clean_odd(row.get('1/X')),
                        '12': self.clean_odd(row.get('1/2')),
                        'x2': self.clean_odd(row.get('X/2')),
                        
                        'iy_ms_1': self.clean_odd(row.get('İY1')),
                        'iy_ms_x': self.clean_odd(row.get('İYX')),
                        'iy_ms_2': self.clean_odd(row.get('İY2')),
                    }
                    
                    matches.append(match_data)
                
                except Exception as e:
                    print(f"⚠️ Satır {index + 1} hatası: {e}")
                    continue
            
            print(f"✅ {len(matches)} maç başarıyla parse edildi")
            return matches
        
        except Exception as e:
            print(f"❌ Sheet okuma hatası: {e}")
            return []
    
    def save_json(self, matches, date_str):
        try:
            output = {
                'date': date_str,
                'timestamp': datetime.now().isoformat(),
                'total_matches': len(matches),
                'matches': matches
            }
            
            json_filename = f"{date_str}.json"
            json_path = os.path.join(self.output_folder, json_filename)
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            
            print(f"💾 JSON kaydedildi: {json_path}")
            return True
        
        except Exception as e:
            print(f"❌ JSON kaydetme hatası: {e}")
            return False
    
    def convert_file(self, excel_file):
        try:
            print(f"\n📂 '{excel_file}' işleniyor...")
            
            xls = pd.ExcelFile(excel_file)
            sheet_names = xls.sheet_names
            
            print(f"📋 {len(sheet_names)} sheet bulundu: {sheet_names}")
            
            success_count = 0
            
            for sheet_name in sheet_names:
                try:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    
                    if any(char.isdigit() for char in sheet_name):
                        date_str = sheet_name.strip()
                    else:
                        filename = os.path.basename(excel_file)
                        date_str = filename.replace('.xlsx', '').replace('.xls', '')
                    
                    matches = self.parse_sheet(df, sheet_name)
                    
                    if matches:
                        if self.save_json(matches, date_str):
                            success_count += 1
                    
                    print("-" * 60)
                
                except Exception as e:
                    print(f"⚠️ Sheet '{sheet_name}' hatası: {e}")
                    continue
            
            print(f"✅ {success_count}/{len(sheet_names)} sheet başarıyla dönüştürüldü!\n")
            return success_count > 0
        
        except Exception as e:
            print(f"❌ Excel dosyası okuma hatası: {e}")
            return False
    
    def convert_all_files(self):
        try:
            excel_files = glob.glob(os.path.join(self.excel_folder, "*.xlsx"))
            excel_files += glob.glob(os.path.join(self.excel_folder, "*.xls"))
            
            if not excel_files:
                print(f"⚠️ '{self.excel_folder}' klasöründe Excel dosyası bulunamadı!")
                return
            
            print(f"\n🔍 {len(excel_files)} Excel dosyası bulundu")
            print("=" * 80)
            
            total_success = 0
            for excel_file in excel_files:
                if self.convert_file(excel_file):
                    total_success += 1
            
            print("=" * 80)
            print(f"🎉 TOPLAM: {total_success}/{len(excel_files)} Excel dosyası başarıyla işlendi!")
            
            json_files = glob.glob(os.path.join(self.output_folder, "*.json"))
            if json_files:
                print(f"\n📄 Oluşturulan JSON dosyaları ({len(json_files)} adet):")
                for json_file in sorted(json_files):
                    print(f"   ✓ {os.path.basename(json_file)}")
        
        except Exception as e:
            print(f"❌ Toplu dönüştürme hatası: {e}")
    
    def display_sample_data(self, json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print("\n" + "=" * 80)
            print(f"📋 ÖRNEK VERİ: {os.path.basename(json_file)}")
            print("=" * 80)
            print(f"📅 Tarih: {data['date']}")
            print(f"⚽ Toplam Maç: {data['total_matches']}")
            print("\n🏆 İLK 3 MAÇ:")
            
            for i, match in enumerate(data['matches'][:3], 1):
                print(f"\n  {i}. {match['home_team']} vs {match['away_team']}")
                print(f"     ⏰ {match['saat']} | 🏟️ {match['lig']}")
                print(f"     MS: 1={match['ms_1']} X={match['ms_x']} 2={match['ms_2']}")
                print(f"     KG Var: {match['kg_var']} | 2.5Ü: {match['ust_2_5']}")
        
        except Exception as e:
            print(f"❌ Veri gösterme hatası: {e}")

def main():
    print("\n" + "=" * 80)
    print("🤖 EXCEL → JSON OTOMATİK DÖNÜŞTÜRÜCÜ BOT")
    print("=" * 80)
    print("📂 Excel Klasörü: Mevcut klasör (.)")
    print("📂 JSON Klasörü: json_output/")
    print("=" * 80)
    
    converter = ExcelToJsonConverter(
        excel_folder=".",
        output_folder="json_output"
    )
    
    converter.convert_all_files()
    
    json_files = sorted(glob.glob(os.path.join(converter.output_folder, "*.json")))
    if json_files:
        converter.display_sample_data(json_files[0])

if __name__ == "__main__":
    main()