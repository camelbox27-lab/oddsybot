import json
import os
import glob
import pandas as pd
from datetime import datetime

# 🔥 Firebase ekle
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase başlat
cred = credentials.Certificate("../serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def filter_matches():
    today = datetime.now().strftime("%d.%m.%Y")
    
    # Merged klasöründeki tüm JSON dosyalarını bul
    merged_files = glob.glob("../merged_json/*.json")
    
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
    
    # İLK YARI GOL LİSTESİ
    ilk_yari_gol_listesi = []
    for match in all_matches:
        oran = match.get('beraberlik_orani')
        if oran and 3.50 <= oran <= 8.00:
            ilk_yari_gol_listesi.append({
                "home_team": match.get('home_team', ''),
                "away_team": match.get('away_team', ''),
                "saat": match.get('saat', '')
            })
    
    # GÜNÜN TERCİHLERİ
    gunun_tercihleri = []
    
    # 2.5 Üst
    ust_25_oranlari = [4.00, 4.10, 4.33, 4.50, 4.75]
    for match in all_matches:
        oran = match.get('beraberlik_orani')
        if oran in ust_25_oranlari and match.get('2_5_ust'):
            gunun_tercihleri.append({
                "home_team": match.get('home_team', ''),
                "away_team": match.get('away_team', ''),
                "saat": match.get('saat', ''),
                "kategori": "2.5 Üst",
                "2_5_ust": match['2_5_ust']
            })
    
    # 3.5 Üst
    ust_35_oranlari = [5.00, 5.25, 5.75, 6.00, 7.00, 8.00]
    for match in all_matches:
        oran = match.get('beraberlik_orani')
        if oran in ust_35_oranlari and match.get('3_5_ust'):
            gunun_tercihleri.append({
                "home_team": match.get('home_team', ''),
                "away_team": match.get('away_team', ''),
                "saat": match.get('saat', ''),
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
                "home_team": match.get('home_team', ''),
                "away_team": match.get('away_team', ''),
                "saat": match.get('saat', ''),
                "kategori": "MS 5.5 Üst",
                "ms_5_5_ust": match['ms_5_5_ust']
            })
    
    # 🔥 FIREBASE'E KAYDET (JSON yerine)
    print("\n🔥 Firebase'e kaydediliyor...")
    
    # Önce eski verileri temizle (opsiyonel)
    # batch = db.batch()
    # old_docs = db.collection('predictions').where('categoryKey', 'in', ['ilk-yari-gol', 'gunun-tercihleri', 'gunun-surprizleri']).stream()
    # for doc in old_docs:
    #     batch.delete(doc.reference)
    # batch.commit()
    
    # İlk Yarı Gol
    for match in ilk_yari_gol_listesi:
        db.collection('predictions').add({
            'categoryKey': 'ilk-yari-gol',
            'homeTeam': match['home_team'],
            'awayTeam': match['away_team'],
            'saat': match['saat'],
            'createdAt': firestore.SERVER_TIMESTAMP
        })
    
    # Günün Tercihleri
    for match in gunun_tercihleri:
        db.collection('predictions').add({
            'categoryKey': 'gunun-tercihleri',
            'homeTeam': match['home_team'],
            'awayTeam': match['away_team'],
            'saat': match['saat'],
            'kategori': match['kategori'],
            '2_5_ust': match.get('2_5_ust'),
            '3_5_ust': match.get('3_5_ust'),
            'createdAt': firestore.SERVER_TIMESTAMP
        })
    
    # Günün Sürprizleri
    for match in gunun_surprizleri:
        db.collection('predictions').add({
            'categoryKey': 'gunun-surprizleri',
            'homeTeam': match['home_team'],
            'awayTeam': match['away_team'],
            'saat': match['saat'],
            'kategori': match['kategori'],
            'ms_5_5_ust': match['ms_5_5_ust'],
            'createdAt': firestore.SERVER_TIMESTAMP
        })
    
    print(f"\n✅ FIREBASE'E KAYDEDİLDİ!")
    print(f"📋 İlk Yarı Gol: {len(ilk_yari_gol_listesi)} maç")
    print(f"⭐ Günün Tercihleri: {len(gunun_tercihleri)} maç")
    print(f"🔥 Günün Sürprizleri: {len(gunun_surprizleri)} maç")
    
    # Excel'e de kaydet (yedek)
    output_dir = "filtered"
    os.makedirs(output_dir, exist_ok=True)
    
    if ilk_yari_gol_listesi:
        df = pd.DataFrame(ilk_yari_gol_listesi)
        df.to_excel(f"{output_dir}/ilk_yari_gol_{today}.xlsx", index=False)
    
    if gunun_tercihleri:
        df = pd.DataFrame(gunun_tercihleri)
        df.to_excel(f"{output_dir}/gunun_tercihleri_{today}.xlsx", index=False)
    
    if gunun_surprizleri:
        df = pd.DataFrame(gunun_surprizleri)
        df.to_excel(f"{output_dir}/gunun_surprizleri_{today}.xlsx", index=False)

if __name__ == "__main__":
    filter_matches()