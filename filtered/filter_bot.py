import json
import os
import glob
import pandas as pd
from datetime import datetime, timezone
import pytz

def filter_matches():
    today = datetime.now().strftime("%d.%m.%Y")

    # Merged klasorundeki BUGUNUN JSON dosyasini bul
    base_dir = os.path.dirname(os.path.abspath(__file__))
    merged_dir = os.path.join(base_dir, '..', 'merged', 'merged_json')
    merged_file = os.path.join(merged_dir, f"merged_{today}.json")

    if not os.path.exists(merged_file):
        # Fallback: en guncel merged dosyayi kullan (site bos kalmasin)
        candidates = sorted(glob.glob(os.path.join(merged_dir, "merged_*.json")), reverse=True)
        if not candidates:
            print(f"Bugun ({today}) icin merged dosyasi bulunamadi: {merged_file}")
            return
        merged_file = candidates[0]
        print(f"[WARN] Bugunun merged dosyasi yok, en guncel dosya kullaniliyor: {os.path.basename(merged_file)}")

    all_matches = []

    try:
        with open(merged_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_matches.extend(data.get('matches', []))
    except Exception as e:
        print(f"Dosya okuma hatasi ({merged_file}): {e}")

    print(f"{len(all_matches)} mac yuklendi")

    # ILK YARI GOL LISTESI
    ilk_yari_gol_listesi = []
    for match in all_matches:
        oran = match.get('beraberlik_orani')
        if oran and 3.50 <= oran <= 8.00:
            ilk_yari_gol_listesi.append({
                "home_team": match.get('home_team', ''),
                "away_team": match.get('away_team', ''),
                "saat": match.get('saat', '')
            })

    # GUNUN TERCIHLERI
    gunun_tercihleri = []

    ust_25_oranlari = [4.00, 4.10, 4.33, 4.50, 4.75]
    for match in all_matches:
        oran = match.get('beraberlik_orani')
        if oran in ust_25_oranlari and match.get('2_5_ust'):
            gunun_tercihleri.append({
                "home_team": match.get('home_team', ''),
                "away_team": match.get('away_team', ''),
                "saat": match.get('saat', ''),
                "kategori": "2.5 Ust",
                "2_5_ust": match['2_5_ust']
            })

    ust_35_oranlari = [5.00, 5.25, 5.75, 6.00, 7.00, 8.00]
    for match in all_matches:
        oran = match.get('beraberlik_orani')
        if oran in ust_35_oranlari and match.get('3_5_ust'):
            gunun_tercihleri.append({
                "home_team": match.get('home_team', ''),
                "away_team": match.get('away_team', ''),
                "saat": match.get('saat', ''),
                "kategori": "3.5 Ust",
                "3_5_ust": match['3_5_ust']
            })

    # GUNUN SURPRIZLERI
    gunun_surprizleri = []

    # MS 5.5 Ust (mevcut kural)
    surpriz_oranlari = [4.50, 4.75, 5.00, 5.25, 5.75, 6.00, 7.00, 8.00]
    for match in all_matches:
        oran = match.get('beraberlik_orani')
        if oran in surpriz_oranlari and match.get('ms_5_5_ust'):
            gunun_surprizleri.append({
                "home_team": match.get('home_team', ''),
                "away_team": match.get('away_team', ''),
                "saat": match.get('saat', ''),
                "kategori": "MS 5.5 Ust",
                "ms_5_5_ust": match['ms_5_5_ust']
            })

    # IY KG VAR (yeni kural: beraberlik 3.50 / 3.60 / 3.75 / 3.80)
    iy_kg_oranlari = [3.50, 3.60, 3.75, 3.80]
    for match in all_matches:
        oran = match.get('beraberlik_orani')
        if oran in iy_kg_oranlari and match.get('iy_kg_var') and match['iy_kg_var'] > 0:
            gunun_surprizleri.append({
                "home_team": match.get('home_team', ''),
                "away_team": match.get('away_team', ''),
                "saat": match.get('saat', ''),
                "kategori": "IY KG Var",
                "iy_kg_var": match['iy_kg_var']
            })

    # JSON DOSYALARINA KAYDET (public/data/ klasorune)
    print("\nJSON dosyalarina kaydediliyor...")

    # Repo root: bot/filtered/ -> bot/ -> TahminApp/
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    data_dir = os.path.join(repo_root, 'public', 'data')
    os.makedirs(data_dir, exist_ok=True)

    # GMT+3 (Türkiye) yerel saat
    tr_tz = pytz.timezone('Europe/Istanbul')
    now_iso = datetime.now(tr_tz).isoformat()

    # halfTimeGoals.json
    half_time_data = []
    for i, match in enumerate(ilk_yari_gol_listesi):
        half_time_data.append({
            'id': f"htg-{i}-{match['home_team']}-{match['away_team']}",
            'homeTeam': match['home_team'],
            'awayTeam': match['away_team'],
            'saat': match['saat'],
            'createdAt': now_iso
        })

    with open(os.path.join(data_dir, 'halfTimeGoals.json'), 'w', encoding='utf-8') as f:
        json.dump(half_time_data, f, ensure_ascii=False, indent=2)

    # dailyChoices.json
    daily_choices_data = []
    for i, match in enumerate(gunun_tercihleri):
        item = {
            'id': f"dc-{i}-{match['home_team']}-{match['away_team']}",
            'homeTeam': match['home_team'],
            'awayTeam': match['away_team'],
            'saat': match['saat'],
            'kategori': match['kategori'],
            'createdAt': now_iso
        }
        if match.get('2_5_ust'):
            item['2_5_ust'] = match['2_5_ust']
        if match.get('3_5_ust'):
            item['3_5_ust'] = match['3_5_ust']
        daily_choices_data.append(item)

    with open(os.path.join(data_dir, 'dailyChoices.json'), 'w', encoding='utf-8') as f:
        json.dump(daily_choices_data, f, ensure_ascii=False, indent=2)

    # dailySurprises.json
    daily_surprises_data = []
    for i, match in enumerate(gunun_surprizleri):
        item = {
            'id': f"ds-{i}-{match['home_team']}-{match['away_team']}",
            'homeTeam': match['home_team'],
            'awayTeam': match['away_team'],
            'saat': match['saat'],
            'kategori': match['kategori'],
            'createdAt': now_iso
        }
        if match.get('ms_5_5_ust'):
            item['ms_5_5_ust'] = match['ms_5_5_ust']
        if match.get('iy_kg_var'):
            item['iy_kg_var'] = match['iy_kg_var']
        daily_surprises_data.append(item)

    with open(os.path.join(data_dir, 'dailySurprises.json'), 'w', encoding='utf-8') as f:
        json.dump(daily_surprises_data, f, ensure_ascii=False, indent=2)

    print(f"\nJSON DOSYALARINA KAYDEDILDI!")
    print(f"Ilk Yari Gol (halfTimeGoals.json): {len(ilk_yari_gol_listesi)} mac")
    print(f"Gunun Tercihleri (dailyChoices.json): {len(gunun_tercihleri)} mac")
    print(f"Gunun Surprizleri (dailySurprises.json): {len(gunun_surprizleri)} mac")

    # IY KG ayrintisi
    iy_kg_count = sum(1 for m in gunun_surprizleri if m['kategori'] == 'IY KG Var')
    ms55_count = sum(1 for m in gunun_surprizleri if m['kategori'] == 'MS 5.5 Ust')
    print(f"  - MS 5.5 Ust: {ms55_count}")
    print(f"  - IY KG Var: {iy_kg_count}")

    print(f"\nDosya yolu: {data_dir}")

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
