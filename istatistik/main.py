"""
ANA KONTROL SCRIPTI - Tüm İşlemleri Sırayla Çalıştırır
Kullanım: python main.py
"""

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

def print_header(text):
    """Başlık yazdır"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def run_script(script_name, args=None):
    """Script'i çalıştır ve sonucu döndür"""
    try:
        cmd = [sys.executable, script_name]
        if args:
            cmd.extend(args)
        
        print(f"🚀 Çalıştırılıyor: {script_name}")
        start_time = time.time()
        
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)
        
        elapsed = time.time() - start_time
        print(f"✅ {script_name} tamamlandı ({elapsed:.1f} saniye)")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ {script_name} HATA: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ {script_name} bulunamadı!")
        return False
    except Exception as e:
        print(f"❌ Beklenmeyen hata ({script_name}): {e}")
        return False

def check_files():
    """Gerekli dosyaları kontrol et"""
    required_files = [
        "scraper.py",
        "excel_to_json.py", 
        "upload_to_firebase.py"
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        print("❌ Eksik dosyalar:")
        for f in missing:
            print(f"   - {f}")
        return False
    
    print("✅ Tüm scriptler mevcut")
    return True

def main():
    print_header("🎯 KART & KORNER VERİ İŞLEME PIPELINE")
    print(f"⏰ Başlangıç: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
    
    # Dosya kontrolü
    if not check_files():
        print("\n❌ Gerekli dosyalar eksik! İşlem iptal edildi.")
        return
    
    results = {}
    
    # ADIM 1: Web Scraping (Kart & Korner Verileri)
    print_header("ADIM 1/3: WEB SCRAPING")
    print("📊 adamchoi.co.uk'dan veriler çekiliyor...")
    results['scraper'] = run_script("scraper.py")
    
    if not results['scraper']:
        print("\n⚠️ Scraping başarısız, devam edilsin mi? (e/h)")
        choice = input().lower()
        if choice != 'e':
            print("❌ İşlem kullanıcı tarafından durduruldu.")
            return
    
    time.sleep(2)
    
    # ADIM 2: Excel → JSON Dönüşümü
    print_header("ADIM 2/3: EXCEL → JSON DÖNÜŞÜMÜ")
    print("📄 Excel dosyaları JSON formatına çevriliyor...")
    results['converter'] = run_script("excel_to_json.py", ["--tip", "hepsi"])
    
    if not results['converter']:
        print("\n❌ JSON dönüşümü başarısız! Firebase yüklemesi yapılamaz.")
        print_summary(results)
        return
    
    time.sleep(2)
    
    # ADIM 3: Firebase Yükleme
    print_header("ADIM 3/3: FIREBASE YÜKLEME")
    print("☁️ Veriler Firebase'e yükleniyor...")
    
    # firebase-key.json kontrolü
    if not Path("firebase-key.json").exists():
        print("\n⚠️ firebase-key.json bulunamadı!")
        print("Firebase yüklemesi atlanıyor...")
        results['firebase'] = False
    else:
        results['firebase'] = run_script("upload_to_firebase.py")
    
    # ÖZET
    print_summary(results)

def print_summary(results):
    """İşlem özetini yazdır"""
    print_header("📋 İŞLEM ÖZETİ")
    
    steps = [
        ("Web Scraping", results.get('scraper', False)),
        ("JSON Dönüşümü", results.get('converter', False)),
        ("Firebase Yükleme", results.get('firebase', False))
    ]
    
    for step_name, success in steps:
        status = "✅ BAŞARILI" if success else "❌ BAŞARISIZ"
        print(f"   {step_name:20s} : {status}")
    
    success_count = sum(1 for _, success in steps if success)
    total = len(steps)
    
    print(f"\n📊 Sonuç: {success_count}/{total} adım başarılı")
    
    if success_count == total:
        print("\n🎉 TÜM İŞLEMLER TAMAMLANDI!")
    elif success_count > 0:
        print("\n⚠️ Bazı işlemler başarısız oldu.")
    else:
        print("\n❌ Hiçbir işlem tamamlanamadı!")
    
    print(f"\n⏰ Bitiş: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ İşlem kullanıcı tarafından durduruldu (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
        import traceback
        traceback.print_exc()