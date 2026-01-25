"""
FUTBOL BOT PIPELINE - TÜM BOTLARI ÇALIŞTIRIR
C:\bot\main.py
"""
import subprocess
import os
from datetime import datetime

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def main():
    print_header("🎯 FUTBOL BOT PIPELINE BAŞLIYOR")
    print(f"⏰ Başlangıç: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
    
    start_dir = os.getcwd()
    results = []
    
    try:
        # 1. DROPPING ODDS BOT
        print_header("1/5: ORAN DÜŞEN MAÇLAR")
        try:
            subprocess.run(['python', 'dropping_odds_bot.py'], check=True)
            results.append(("Dropping Odds", True))
        except Exception as e:
            print(f"❌ Hata: {e}")
            results.append(("Dropping Odds", False))
        
        # 2. SOFA BOT
        print_header("2/5: MAÇ VERİLERİ (SOFA)")
        try:
            os.chdir('sofa')
            subprocess.run(['python', 'bet365data.py'], check=True)
            results.append(("Sofa Bot", True))
        except Exception as e:
            print(f"❌ Hata: {e}")
            results.append(("Sofa Bot", False))
        finally:
            os.chdir(start_dir)
        
        # 3. EXCEL TO JSON
        print_header("3/5: EXCEL → JSON DÖNÜŞÜMÜ")
        try:
            os.chdir('mackolik-excel-json')
            subprocess.run(['python', 'excel_to_json_bot.py'], check=True)
            results.append(("Excel to JSON", True))
        except Exception as e:
            print(f"❌ Hata: {e}")
            results.append(("Excel to JSON", False))
        finally:
            os.chdir(start_dir)
        
        # 4. MERGER
        print_header("4/5: VERİLER BİRLEŞTİRİLİYOR")
        try:
            os.chdir('merged')
            subprocess.run(['python', 'match_merger_bot.py'], check=True)
            results.append(("Merger", True))
        except Exception as e:
            print(f"❌ Hata: {e}")
            results.append(("Merger", False))
        finally:
            os.chdir(start_dir)
        
        # 5. FILTER
        print_header("5/5: FİLTRELER UYGULANYOR")
        try:
            subprocess.run(['python', 'filter_bot.py'], check=True)
            results.append(("Filter", True))
        except Exception as e:
            print(f"❌ Hata: {e}")
            results.append(("Filter", False))
        
        # ÖZET
        print_header("📋 İŞLEM ÖZETİ")
        success_count = 0
        for step_name, success in results:
            status = "✅ BAŞARILI" if success else "❌ BAŞARISIZ"
            print(f"   {step_name:20s} : {status}")
            if success:
                success_count += 1
        
        print(f"\n📊 Sonuç: {success_count}/{len(results)} adım başarılı")
        
        if success_count == len(results):
            print("\n🎉 TÜM İŞLEMLER TAMAMLANDI!")
        else:
            print("\n⚠️ Bazı adımlar başarısız oldu.")
        
        print(f"\n⏰ Bitiş: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ GENEL HATA: {e}")
        import traceback
        traceback.print_exc()
    finally:
        os.chdir(start_dir)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ İşlem durduruldu (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Kritik hata: {e}")