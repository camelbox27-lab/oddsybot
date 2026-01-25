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
    
    def extract_date_from_sheet(self, sheet_name, filename):
        """Sheet veya dosya adından tarihi çıkar"""
        # Önce sheet adına bak
        if any(char.isdigit() for char in sheet_name):
            # Sheet adında tarih varsa (örn: "09.01.2026")
            parts = sheet_name.strip().split('.')
            if len(parts) == 3:
                try:
                    # Tarihi doğrula
                    datetime.strptime(sheet_name.strip(), '%d.%m.%Y')
                    return sheet_name.strip()
                except:
                    pass
        
        # Sheet adında tarih yoksa dosya adına bak
        base_name = os.path.basename(filename)
        date_str = base_name.replace('.xlsx', '').replace('.xls', '')
        
        # Dosya adı tarih formatında mı kontrol et
        parts = date_str.split('.')
        if len(parts) == 3:
            try:
                datetime.strptime(date_str, '%d.%m.%Y')
                return date_str
            except:
                pass
        
        # Hiçbiri yoksa bugünün tarihini kullan
        return datetime.now().strftime('%d.%m.%Y')
    
    def parse_sheet(self, df, sheet_name=""):
        try:
            print(f"📊 '{sheet_name}' - Toplam {len(df)} satır bulundu")
            
            matches = []
            
            for index, row in df.iterrows():
                try:
                    # İlk sütunları ada göre al
                    home_team = self.clean_team_name(row.iloc[0] if len(row) > 0 else '')
                    away_team = self.clean_team_name(row.iloc[1] if len(row) > 1 else '')
                    
                    if not home_team or not away_team:
                        continue
                    
                    match_data = {
                        'home_team': home_team,
                        'away_team': away_team,
                        'saat': str(row.iloc[12] if len(row) > 12 else ''),  # Saat sütunu
                        'lig': '',
                        
                        # MS oranları (C, D, E)
                        'ms_1': self.clean_odd(row.iloc[2] if len(row) > 2 else None),
                        'ms_x': self.clean_odd(row.iloc[3] if len(row) > 3 else None),
                        'ms_2': self.clean_odd(row.iloc[4] if len(row) > 4 else None),
                        
                        # Karşılıklı Gol (F, G)
                        'kg_var': self.clean_odd(row.iloc[5] if len(row) > 5 else None),
                        'kg_yok': self.clean_odd(row.iloc[6] if len(row) > 6 else None),
                        
                        # 2.5 (H=Alt, I=Üst)
                        'alt_2_5': self.clean_odd(row.iloc[7] if len(row) > 7 else None),
                        'ust_2_5': self.clean_odd(row.iloc[8] if len(row) > 8 else None),
                        
                        # 3.5 (J=Alt, K=Üst)
                        'alt_3_5': self.clean_odd(row.iloc[9] if len(row) > 9 else None),
                        'ust_3_5': self.clean_odd(row.iloc[10] if len(row) > 10 else None),
                        
                        # 5.5 (L)
                        'ust_5_5': self.clean_odd(row.iloc[11] if len(row) > 11 else None),
                        'alt_5_5': None,
                        
                        '1x': None,
                        '12': None,
                        'x2': None,
                        
                        'iy_ms_1': None,
                        'iy_ms_x': None,
                        'iy_ms_2': None,
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
            
            # Dosya adını tarih olarak kaydet
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
                    # 2. satırdan itibaren oku (ilk satır birleşik başlık)
                    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=1)
                    
                    # Tarihi akıllıca çıkar
                    date_str = self.extract_date_from_sheet(sheet_name, excel_file)
                    print(f"📅 Tespit edilen tarih: {date_str}")
                    
                    matches = self.parse_sheet(df, sheet_name)
                    
                    if matches:
                        if self.save_json(matches, date_str):
                            success_count += 1
                    
                    print("-" * 60)
                
                except Exception as e:
                    print(f"⚠️ Sheet '{sheet_name}' hatası: {e}")
                    import traceback
                    traceback.print_exc()
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
                print(f"     ⏰ {match['saat']}")
                print(f"     MS: 1={match['ms_1']} X={match['ms_x']} 2={match['ms_2']}")
                print(f"     2.5: Üst={match['ust_2_5']} Alt={match['alt_2_5']}")
                print(f"     3.5: Üst={match['ust_3_5']} Alt={match['alt_3_5']}")
        
        except Exception as e:
            print(f"❌ Veri gösterme hatası: {e}")

def main():
    print("\n" + "=" * 80)
    print("🤖 EXCEL → JSON OTOMATİK DÖNÜŞTÜRÜCÜ BOT (INDEX BAZLI)")
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