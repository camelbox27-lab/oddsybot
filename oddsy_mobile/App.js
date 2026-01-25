import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, ScrollView, SafeAreaView, StatusBar, ActivityIndicator, TextInput, Alert } from 'react-native';
import { Play, Terminal, Activity, Cpu, Github } from 'lucide-react-native';

// ==========================================
// AYARLAR (Burayı KENDİ BİLGİLERİNLE Doldur)
// ==========================================
const DEFAULT_REPO = 'camelbox27-lab/oddsybot'; // Repo Adı
const DEFAULT_TOKEN = ''; // <-- TOKEN'I BURAYA YAPIŞTIR (örn: 'ghp_Ax7...')
// ==========================================

export default function App() {
  // Varsayılan Değerler
  const [repoName, setRepoName] = useState(DEFAULT_REPO);
  const [githubToken, setGithubToken] = useState(DEFAULT_TOKEN);

  const [running, setRunning] = useState(null);
  const [logs, setLogs] = useState(['GitHub Actions Konsolu Hazır.']);

  const addLog = (m) => {
    setLogs(p => [...p.slice(-4), `> ${new Date().toLocaleTimeString()}: ${m}`]);
  };

  const runBot = async (type) => {
    if (!repoName || !githubToken) {
      Alert.alert("Eksik Bilgi", "Lütfen Repo Adı ve GitHub Token (PAT) girin.");
      return;
    }
    if (running) return;

    setRunning(type);
    addLog(`GitHub Action Tetikleniyor: ${type === 'main' ? 'Ana Bot' : 'İstatistik'}...`);

    try {
      // GitHub API Dispatch Endpoint
      const url = `https://api.github.com/repos/${repoName}/actions/workflows/run_bot.yml/dispatches`;

      const payload = {
        ref: 'main', // veya 'master', hangi branch'te çalışıyorsan
        inputs: {
          bot_type: type // 'main' veya 'stats'
        }
      };

      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'Accept': 'application/vnd.github.v3+json',
          'Authorization': `Bearer ${githubToken}`,
          'Content-Type': 'application/json',
          'User-Agent': 'OddsBot-Mobile'
        },
        body: JSON.stringify(payload)
      });

      if (res.status === 204) {
        addLog(`✅ BAŞARILI: Action tetiklendi! GitHub'dan izleyebilirsiniz.`);
        addLog(`(Yaklaşık 30-60sn içinde başlar)`);
      } else {
        const errData = await res.json();
        addLog(`❌ HATA: ${errData.message || 'Yetki veya Repo hatası'}`);
      }
    } catch (err) {
      addLog(`❌ Bağlantı hatası: ${err.message}`);
    } finally {
      setRunning(null);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />

      <View style={styles.header}>
        <Text style={styles.logo}>ODDSY</Text>
        <Text style={styles.subtitle}>GITHUB ACTION YÖNETİCİSİ</Text>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>

        {/* GITHUB AYAR ALANI */}
        <View style={styles.inputSection}>
          <Text style={styles.inputLabel}>GITHUB REPO (kullanici/repo)</Text>
          <View style={styles.inputContainer}>
            <Github color="#94a3b8" size={20} />
            <TextInput
              style={styles.input}
              placeholder="camelbox27-lab/oddsybot"
              placeholderTextColor="#475569"
              value={repoName}
              onChangeText={setRepoName}
              autoCapitalize="none"
              autoCorrect={false}
            />
          </View>
        </View>

        <View style={styles.inputSection}>
          <Text style={styles.inputLabel}>GITHUB TOKEN (PAT - Workflow Yetkili)</Text>
          <View style={styles.inputContainer}>
            <Terminal color="#94a3b8" size={20} />
            <TextInput
              style={styles.input}
              placeholder="ghp_xxxxxxxxxxxx"
              placeholderTextColor="#475569"
              value={githubToken}
              onChangeText={setGithubToken}
              autoCapitalize="none"
              secureTextEntry
            />
          </View>
        </View>

        <TouchableOpacity
          style={[styles.card, running === 'main' && styles.cardDisabled]}
          onPress={() => runBot('main')}
          disabled={running !== null}
        >
          <View style={styles.cardHeader}>
            <Cpu color="#fbbf24" size={24} />
            <Text style={styles.cardTitle}>Ana Bot Başlat</Text>
          </View>
          <Text style={styles.cardDesc}>GitHub sunucularında (ubuntu) Ana Botu (Sofa, Oran, Excel) çalıştırır.</Text>
          <View style={[styles.button, { backgroundColor: '#059669' }]}>
            {running === 'main' ? (
              <ActivityIndicator color="white" />
            ) : (
              <>
                <Play color="white" size={18} fill="white" />
                <Text style={styles.buttonText}>TETİKLE (MAIN)</Text>
              </>
            )}
          </View>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.card, running === 'stats' && styles.cardDisabled]}
          onPress={() => runBot('stats')}
          disabled={running !== null}
        >
          <View style={styles.cardHeader}>
            <Activity color="#60a5fa" size={24} />
            <Text style={styles.cardTitle}>İstatistik Başlat</Text>
          </View>
          <Text style={styles.cardDesc}>GitHub sunucularında İstatistik (Scraper, Kart/Korner) botunu çalıştırır.</Text>
          <View style={[styles.button, { backgroundColor: '#1d4ed8' }]}>
            {running === 'stats' ? (
              <ActivityIndicator color="white" />
            ) : (
              <>
                <Play color="white" size={18} fill="white" />
                <Text style={styles.buttonText}>TETİKLE (STATS)</Text>
              </>
            )}
          </View>
        </TouchableOpacity>

        <View style={styles.console}>
          <View style={styles.consoleHeader}>
            <Terminal color="#94a3b8" size={14} />
            <Text style={styles.consoleHeaderText}>LOGLAR</Text>
          </View>
          {logs.map((log, i) => (
            <Text key={i} style={styles.logText}>{log}</Text>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#020f0e',
  },
  header: {
    padding: 24,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#112220',
  },
  logo: {
    fontSize: 32,
    fontWeight: '900',
    color: '#fbbf24',
    letterSpacing: 2,
  },
  subtitle: {
    fontSize: 12,
    color: '#94a3b8',
    letterSpacing: 4,
    marginTop: 4,
    fontWeight: '600',
  },
  scrollContent: {
    padding: 20,
  },
  inputSection: {
    marginBottom: 20,
  },
  inputLabel: {
    color: '#94a3b8',
    fontSize: 10,
    fontWeight: 'bold',
    marginBottom: 8,
    marginLeft: 4,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#061614',
    borderWidth: 1,
    borderColor: '#334155',
    borderRadius: 12,
    paddingHorizontal: 12,
    height: 50,
  },
  input: {
    flex: 1,
    color: 'white',
    marginLeft: 10,
    fontSize: 14,
  },
  card: {
    backgroundColor: '#061614',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#112220',
  },
  cardDisabled: {
    opacity: 0.5,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  cardTitle: {
    color: 'white',
    fontSize: 20,
    fontWeight: '700',
    marginLeft: 12,
  },
  cardDesc: {
    color: '#94a3b8',
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 20,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 14,
    borderRadius: 12,
    gap: 8,
  },
  buttonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
  },
  console: {
    backgroundColor: '#000',
    borderRadius: 12,
    padding: 16,
    marginTop: 10,
    height: 180,
    borderWidth: 1,
    borderColor: '#334155',
  },
  consoleHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
    gap: 6,
  },
  consoleHeaderText: {
    color: '#64748b',
    fontSize: 10,
    fontWeight: 'bold',
  },
  logText: {
    color: '#4ade80',
    fontFamily: 'monospace',
    fontSize: 12,
    marginBottom: 4,
  }
});

