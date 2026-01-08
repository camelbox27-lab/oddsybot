import json
import os
from difflib import SequenceMatcher
from datetime import datetime
import glob

class MatchMergerBot:
    def __init__(self, mackolik_folder="../mackolik-excel-json/json_output", 
                 sofascore_folder="../sofa", 
                 output_folder="merged_json"):
        self.mackolik_folder = mackolik_folder
        self.sofascore_folder = sofascore_folder
        self.output_folder = output_folder
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            print(f"📁 '{output_folder}' klasörü oluşturuldu")
    
    def similarity(self, a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def normalize_team_name(self, name):
        name = name.lower().strip()
        
        # Özel karakterleri temizle
        name = name.replace("'", "").replace("-", " ").replace(".", "")
        
        # Ortak kelime çıkarmaları
        replacements = {
            'fc': '', 'cf': '', 'sc': '', 'ac': '', 'as': '', 'us': '',
            'cd': '', 'ud': '', 'sd': '', 'sk': '', 'fk': '', 'ca': '',
            'athletic': 'ath', 'united': 'utd', 'sporting': 'sp',
            'olympique': 'ol', 'real': 'r', 'club': '', 'city': '',
            'town': '', 'athletic': 'ath', 'metropolitan': 'metro',
            'phoenix': 'phx', 'wanderers': 'wand', 'rovers': 'rov',
        }
        
        for old, new in replacements.items():
            name = name.replace(f' {old} ', f' {new} ')
            name = name.replace(f' {old}', f' {new}')
            name = name.replace(f'{old} ', f'{new} ')
        
        return ' '.join(name.split())
    
    def find_best_match(self, team_name, candidates):
        normalized_team = self.normalize_team_name(team_name)
        best_match = None
        best_score = 0.0
        
        for candidate in candidates:
            normalized_candidate = self.normalize_team_name(candidate)
            
            # Tam eşleşme
            if normalized_team == normalized_candidate:
                return candidate, 1.0
            
            # Benzerlik skoru
            score = self.similarity(normalized_team, normalized_candidate)
            
            # Bonuslar
            # Bir takım diğerini içeriyorsa
            if normalized_team in normalized_candidate or normalized_candidate in normalized_team:
                score += 0.3
            
            # İlk kelime eşleşmesi (önemli)
            team_words = normalized_team.split()
            candidate_words = normalized_candidate.split()
            if team_words and candidate_words and team_words[0] == candidate_words[0]:
                score += 0.2
            
            # Kelime bazlı eşleşme
            common_words = set(team_words) & set(candidate_words)
            if common_words:
                score += len(common_words) * 0.1
            
            if score > best_score:
                best_score = score
                best_match = candidate
        
        # Minimum %60 benzerlik (düşürüldü)
        if best_score < 0.60:
            return None, best_score
        return best_match, best_score
    
    def load_json(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ JSON okuma hatası ({file_path}): {e}")
            return None
    
    def merge_matches(self, mackolik_file, sofascore_file):
        try:
            if not os.path.exists(mackolik_file):
                print(f"⚠️ Mackolik dosyası bulunamadı: {mackolik_file}")
                return False
            
            if not os.path.exists(sofascore_file):
                print(f"⚠️ Sofascore dosyası bulunamadı: {sofascore_file}")
                return False
            
            mackolik_data = self.load_json(mackolik_file)
            sofascore_data = self.load_json(sofascore_file)
            
            if not mackolik_data or not sofascore_data:
                return False
            
            date_str = mackolik_data.get('date', 'unknown')
            
            print(f"\n📊 {date_str} için eşleştirme başlıyor...")
            print(f"   Mackolik: {mackolik_data.get('total_matches', 0)} maç")
            
            # Sofascore data list ise direkt kullan
            if isinstance(sofascore_data, list):
                sofascore_matches = sofascore_data
            else:
                sofascore_matches = sofascore_data.get('matches', [])
            
            print(f"   Sofascore: {len(sofascore_matches)} maç")
            
            sofascore_dict = {}
            for match in sofascore_matches:
                key = f"{match['home_team']}_{match['away_team']}"
                sofascore_dict[key] = match
            
            merged_matches = []
            unmatched_mackolik = []
            unmatched_sofascore = list(sofascore_dict.keys())
            
            for mackolik_match in mackolik_data.get('matches', []):
                home_team = mackolik_match['home_team']
                away_team = mackolik_match['away_team']
                
                best_home, home_score = self.find_best_match(
                    home_team, 
                    [m['home_team'] for m in sofascore_matches]
                )
                
                best_away, away_score = self.find_best_match(
                    away_team,
                    [m['away_team'] for m in sofascore_matches]
                )
                
                if best_home and best_away and home_score > 0.60 and away_score > 0.60:
                    sofa_key = f"{best_home}_{best_away}"
                    
                    if sofa_key in sofascore_dict:
                        sofascore_match = sofascore_dict[sofa_key]
                        
                        merged_match = {
                            'event_id': sofascore_match.get('event_id'),
                            'date_time': sofascore_match.get('date_time'),
                            'home_team': home_team,
                            'away_team': away_team,
                            'saat': mackolik_match.get('saat'),
                            'beraberlik_orani': sofascore_match.get('draw'),
                            'kg_var': mackolik_match.get('kg_var'),
                            '2_5_ust': mackolik_match.get('ust_2_5'),
                            '3_5_ust': mackolik_match.get('ust_3_5'),
                            'ms_5_5_ust': mackolik_match.get('ust_5_5'),
                        }
                        
                        merged_matches.append(merged_match)
                        
                        if sofa_key in unmatched_sofascore:
                            unmatched_sofascore.remove(sofa_key)
                        
                        print(f"   ✅ {home_team} vs {away_team}")
                else:
                    unmatched_mackolik.append(f"{home_team} vs {away_team}")
                    print(f"   ❌ {home_team} vs {away_team}")
            
            print(f"\n📋 RAPOR:")
            print(f"   ✅ Eşleşen: {len(merged_matches)}")
            print(f"   ❌ Eşleşmeyen: {len(unmatched_mackolik)}")
            
            output_data = {
                'date': date_str,
                'timestamp': datetime.now().isoformat(),
                'total_merged': len(merged_matches),
                'matches': merged_matches
            }
            
            output_file = os.path.join(self.output_folder, f"merged_{date_str}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 JSON kaydedildi: {output_file}")
            return True
        
        except Exception as e:
            print(f"❌ Hata: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def merge_all_dates(self):
        try:
            mackolik_files = glob.glob(os.path.join(self.mackolik_folder, "*.json"))
            
            if not mackolik_files:
                print(f"⚠️ Mackolik klasöründe JSON bulunamadı!")
                return
            
            print(f"\n🔍 {len(mackolik_files)} dosya bulundu")
            print("=" * 80)
            
            success_count = 0
            for mackolik_file in sorted(mackolik_files):
                sofascore_files = glob.glob(os.path.join(self.sofascore_folder, "sofascore_matches_*.json"))
                
                if sofascore_files:
                    sofascore_file = sofascore_files[0]
                    if self.merge_matches(mackolik_file, sofascore_file):
                        success_count += 1
                
                print("-" * 80)
            
            print(f"\n🎉 TOPLAM: {success_count}/{len(mackolik_files)} eşleştirildi!")
        
        except Exception as e:
            print(f"❌ Hata: {e}")

def main():
    print("\n" + "=" * 80)
    print("🤝 MERGER BOT")
    print("=" * 80)
    
    merger = MatchMergerBot(
        mackolik_folder="../mackolik-excel-json/json_output",
        sofascore_folder="../sofa",
        output_folder="merged_json"
    )
    
    merger.merge_all_dates()

if __name__ == "__main__":
    main()