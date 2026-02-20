#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean JSON verilerini siler - filter_bot.py öncesinde çalışır
"""
import os
import json

def clean_old_data():
    """Eski JSON dosyalarını siler"""
    
    repo_root = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(repo_root, 'public', 'data')
    
    print("="*70)
    print("ESKI VERILERI TEMİZLEME")
    print("="*70)
    
    files_to_delete = [
        'halfTimeGoals.json',
        'dailyChoices.json',
        'dailySurprises.json'
    ]
    
    deleted_count = 0
    for filename in files_to_delete:
        filepath = os.path.join(data_dir, filename)
        
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"[DELETE] {filename} silindi")
                deleted_count += 1
            except Exception as e:
                print(f"[ERROR] {filename} silinirken hata: {e}")
        else:
            print(f"[SKIP] {filename} bulunamadı")
    
    print(f"\n[OK] {deleted_count}/{len(files_to_delete)} dosya silindi")
    print("="*70 + "\n")

if __name__ == "__main__":
    clean_old_data()
