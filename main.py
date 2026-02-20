#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FUTBOL BOT PIPELINE - TUM ADIMLAR SIRASIYLA CALISIR

Adimlar:
  1. Oran Dusen Maclar    (dropping_odds_bot.py)
  2. SofaScore Verileri   (sofa/bet365data.py)
  3. Mackolik Verileri    (guncel_bulten.py -> JSON)
  4. Verileri Birlestir   (merged/match_merger_bot.py)
  5. Eski Verileri Temizle (clean.py)
  6. Filtrele + JSON Kaydet (filter_bot.py)  
  7. Git Push (oddsy-data reposuna)

NOT: Firebase KULLANILMAZ. Veriler JSON olarak oddsy-data reposuna push edilir.
     Frontend bu JSON'lari GitHub raw URL'lerinden ceker.
"""
import subprocess
import sys
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# oddsy-data: CI'da ./oddsy-data, lokalde ../oddsy-data
_ci_path = os.path.join(BASE_DIR, 'oddsy-data')
_local_path = os.path.abspath(os.path.join(BASE_DIR, '..', 'oddsy-data'))
ODDSY_DATA_DIR = _ci_path if os.path.exists(_ci_path) else _local_path


def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}")


def run_step(step_name, script_name, work_dir=None):
    """Bir pipeline adimini calistirir."""
    print_header(step_name)
    cwd = work_dir or BASE_DIR
    script_path = os.path.join(cwd, script_name)

    if not os.path.exists(script_path):
        print(f"[ERROR] Script bulunamadi: {script_path}")
        return False

    try:
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=cwd,
            check=True,
            env=env
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {script_name} basarisiz (exit code: {e.returncode})")
        return False
    except Exception as e:
        print(f"[ERROR] {script_name} hatasi: {e}")
        return False


def main():
    print_header("FUTBOL BOT PIPELINE BASLANIYOR")
    print(f"[START] {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print(f"[DIR]   {BASE_DIR}\n")

    # Gerekli klasorleri olustur
    os.makedirs(os.path.join(BASE_DIR, "filtered"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "merged", "merged_json"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "mackolik-excel-json", "json_output"), exist_ok=True)
    os.makedirs(os.path.join(ODDSY_DATA_DIR, "data"), exist_ok=True)

    # Pipeline adimlari: (isim, script, calisma_dizini)
    steps = [
        ("1/6: ORAN DUSEN MACLAR",      "dropping_odds_bot.py", BASE_DIR),
        ("2/6: SOFASCORE VERILERI",      "bet365data.py",        os.path.join(BASE_DIR, "sofa")),
        ("3/6: MACKOLIK VERILERI",       "guncel_bulten.py",     BASE_DIR),
        ("4/6: VERILERI BIRLESTIR",      "match_merger_bot.py",  os.path.join(BASE_DIR, "merged")),
        ("5/6: ESKI VERILERI TEMİZLE",   "clean.py",             BASE_DIR),
        ("6/6: FILTRELE + JSON KAYDET",  "filter_bot.py",        BASE_DIR),
    ]

    results = []
    for step_name, script, cwd in steps:
        success = run_step(step_name, script, cwd)
        results.append((step_name, success))

    # --- OZET ---
    print_header("ISLEM OZETI")

    success_count = 0
    for step_name, success in results:
        status = "[OK]  " if success else "[FAIL]"
        print(f"   {status} {step_name}")
        if success:
            success_count += 1

    print(f"\n[RESULT] {success_count}/{len(results)} adim basarili")

    if success_count == len(results):
        print("\n[SUCCESS] TUM ISLEMLER TAMAMLANDI!")
    else:
        print("\n[WARN] Bazi adimlar basarisiz oldu.")

    # --- GIT PUSH (oddsy-data reposuna) ---
    print_header("7/7: GIT PUSH (oddsy-data reposuna)")

    if os.path.exists(ODDSY_DATA_DIR):
        try:
            today_str = datetime.now().strftime('%d.%m.%Y')
            # Once pull al, conflict onle
            subprocess.run(['git', 'pull', 'origin', 'main', '--rebase'], cwd=ODDSY_DATA_DIR, check=False)
            subprocess.run(['git', 'add', 'data/'], cwd=ODDSY_DATA_DIR, check=True)
            # Degisiklik var mi kontrol et
            diff = subprocess.run(['git', 'diff', '--staged', '--quiet'], cwd=ODDSY_DATA_DIR)
            if diff.returncode != 0:
                subprocess.run(
                    ['git', 'commit', '-m', f'chore: update daily predictions {today_str}'],
                    cwd=ODDSY_DATA_DIR, check=True
                )
                subprocess.run(['git', 'push', 'origin', 'main'], cwd=ODDSY_DATA_DIR, check=True)
                print("[OK] oddsy-data git push basarili! Frontend otomatik guncellenecek.")
            else:
                print("[INFO] Veri degismedi, push gerekmiyor.")
        except Exception as e:
            print(f"[ERROR] Git push hatasi: {e}")
    else:
        print(f"[ERROR] oddsy-data klasoru bulunamadi: {ODDSY_DATA_DIR}")

    print(f"\n[END] {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARN] Islem durduruldu (Ctrl+C)")
    except Exception as e:
        print(f"\n[CRITICAL] Kritik hata: {e}")
        import traceback
        traceback.print_exc()