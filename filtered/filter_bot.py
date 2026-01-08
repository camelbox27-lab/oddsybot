import json
import os
import glob
import pandas as pd
from datetime import datetime

def filter_matches():
    today = datetime.now().strftime("%d.%m.%Y")
    
    # Merged klasöründeki tüm JSON dosyalarını bul
    merged_files = glob.glob("C:/bot/merged/merged_json/*.json")
    
    if not merged_files:
        print(f"❌ Merged klasöründe JSON bulunamadı!")
        return
    
    all_matches = []
    
    # Tüm merged dosyalarını oku
    for merged_file in merged_files:
        try:
            with open(merged_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_matches.extend(data.get('matches', []))
        except Exception as e:
            print(f"⚠️ Dosya okuma hatası ({merged_file}): {e}")
    
    print(f"✅ {len(all_matches)} maç yüklendi")
    
    # İLK YARI GOL LİSTESİ - ORAN YOK
    ilk_yari_gol_listesi = []
    for match in all_matches:
        oran = match.get('beraberlik_orani')
        if oran and 3.50 <= oran <= 8.00:
            ilk_yari_gol_listesi.append({
                "home_team": match['home_team'],
                "away_team": match['away_team'],
                "saat": match['saat']
            })
    
    # GÜNÜN TERCİHLERİ
    gunun_tercihleri = []
    
    # 2.5 Üst
    ust_25_oranlari = [4.00, 4.10, 4.33, 4.50, 4.75]
    for match in all_matches:
        oran = match.get('beraberlik_orani')
        if oran in ust_25_oranlari and match.get('2_5_ust'):
            gunun_tercihleri.append({
                "home_team": match['home_team'],
                "away_team": match['away_team'],
                "kategori": "2.5 Üst",
                "2_5_ust": match['2_5_ust']
            })
    
    # 3.5 Üst
    ust_35_oranlari = [5.00, 5.25, 5.75, 6.00, 7.00, 8.00]
    for match in all_matches:
        oran = match.get('beraberlik_orani')
        if oran in ust_35_oranlari and match.get('3_5_ust'):
            gunun_tercihleri.append({
                "home_team": match['home_team'],
                "away_team": match['away_team'],
                "kategori": "3.5 Üst",
                "3_5_ust": match['3_5_ust']
            })
    
    # GÜNÜN SÜPRİZLERİ
    gunun_surprizleri = []
    surpriz_oranlari = [4.50, 4.75, 5.00, 5.25, 5.75, 6.00, 7.00, 8.00]
    
    for match in all_matches:
        oran = match.get('beraberlik_orani')
        if oran in surpriz_oranlari and match.get('ms_5_5_ust'):
            gunun_surprizleri.append({
                "home_team": match['home_team'],
                "away_team": match['away_team'],
                "kategori": "MS 5.5 Üst",
                "ms_5_5_ust": match['ms_5_5_ust']
            })
    
    # Kaydet (JSON + Excel)
    output_dir = "C:/bot/filtered"
    os.makedirs(output_dir, exist_ok=True)
    
    # İlk Yarı Gol Listesi
    with open(f"{output_dir}/ilk_yari_gol_listesi_{today}.json", 'w', encoding='utf-8') as f:
        json.dump({
            "category": "İlk Yarı Gol Listesi",
            "matches": ilk_yari_gol_listesi
        }, f, ensure_ascii=False, indent=2)
    
    if ilk_yari_gol_listesi:
        df = pd.DataFrame(ilk_yari_gol_listesi)
        df.to_excel(f"{output_dir}/ilk_yari_gol_listesi_{today}.xlsx", index=False)
    
    # Günün Tercihleri
    with open(f"{output_dir}/gunun_tercihleri_{today}.json", 'w', encoding='utf-8') as f:
        json.dump({
            "category": "Günün Tercihleri",
            "matches": gunun_tercihleri
        }, f, ensure_ascii=False, indent=2)
    
    if gunun_tercihleri:
        df = pd.DataFrame(gunun_tercihleri)
        df.to_excel(f"{output_dir}/gunun_tercihleri_{today}.xlsx", index=False)
    
    # Günün Sürprizleri
    with open(f"{output_dir}/gunun_surprizleri_{today}.json", 'w', encoding='utf-8') as f:
        json.dump({
            "category": "Günün Sürprizleri",
            "matches": gunun_surprizleri
        }, f, ensure_ascii=False, indent=2)
    
    if gunun_surprizleri:
        df = pd.DataFrame(gunun_surprizleri)
        df.to_excel(f"{output_dir}/gunun_surprizleri_{today}.xlsx", index=False)
    
    print(f"\n✅ FİLTRELEME TAMAMLANDI!")
    print(f"📋 İlk Yarı Gol Listesi: {len(ilk_yari_gol_listesi)} maç")
    print(f"⭐ Günün Tercihleri: {len(gunun_tercihleri)} maç")
    print(f"🔥 Günün Sürprizleri: {len(gunun_surprizleri)} maç")

if __name__ == "__main__":
    filter_matches()