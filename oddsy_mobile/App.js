import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, ScrollView, SafeAreaView, StatusBar, ActivityIndicator } from 'react-native';
import { Play, Terminal, Activity, Cpu } from 'lucide-react-native';

// Localtunnel adresi (İnternet üzerinden erişim sağlar)
const API_BASE = 'https://sour-yaks-fall.loca.lt';

export default function App() {
  const [running, setRunning] = useState(null);
  const [logs, setLogs] = useState(['ODDSY Global Console Hazır.']);
  const [status, setStatus] = useState('checking');

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/status`);
        if (res.ok) setStatus('online');
        else setStatus('offline');
      } catch (err) {
        setStatus('offline');
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 10000); // 10 saniyede bir kontrol
    return () => clearInterval(interval);
  }, []);

  const addLog = (m) => {
    setLogs(p => [...p.slice(-4), `> ${new Date().toLocaleTimeString()}: ${m}`]);
  };

  const runBot = async (type) => {
    if (running || status === 'offline') return;

    setRunning(type);
    addLog(`Başlatılıyor: ${type === 'oran' ? 'Oran Analiz' : 'Kart/Korner Analiz'}...`);

    try {
      const endpoint = type === 'oran' ? '/api/run-oran' : '/api/run-kart-korner';
      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: {
          'Bypass-Tunnel-Reminder': 'true' // Localtunnel uyarı sayfasını geçmek için
        }
      });
      const data = await res.json();

      if (data.success) {
        addLog(`${type === 'oran' ? 'Oran' : 'Kart/Korner'} analizi tamamlandı.`);
      } else {
        addLog(`HATA: ${data.message || 'Bilinmeyen hata'}`);
      }
    } catch (err) {
      addLog('Bağlantı hatası! Sunucu internete açık mı?');
    } finally {
      setRunning(null);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />

      <View style={styles.header}>
        <Text style={styles.logo}>ODDSY</Text>
        <Text style={styles.subtitle}>GLOBAL KONTROL MERKEZİ</Text>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.statusSection}>
          <View style={[styles.statusDot, { backgroundColor: status === 'online' ? '#4ade80' : '#f87171' }]} />
          <Text style={styles.statusText}>SUNUCU (GLOBAL): {status.toUpperCase()}</Text>
        </View>

        <TouchableOpacity
          style={[styles.card, (running === 'oran' || status === 'offline') && styles.cardDisabled]}
          onPress={() => runBot('oran')}
          disabled={running !== null || status === 'offline'}
        >
          <View style={styles.cardHeader}>
            <Cpu color="#fbbf24" size={24} />
            <Text style={styles.cardTitle}>Oran Analiz</Text>
          </View>
          <Text style={styles.cardDesc}>Python botunu internet üzerinden çalıştırarak güncel oran analizlerini başlatır.</Text>
          <View style={[styles.button, { backgroundColor: '#059669' }]}>
            {running === 'oran' ? (
              <ActivityIndicator color="white" />
            ) : (
              <>
                <Play color="white" size={18} fill="white" />
                <Text style={styles.buttonText}>ANALİZİ BAŞLAT</Text>
              </>
            )}
          </View>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.card, (running === 'kart' || status === 'offline') && styles.cardDisabled]}
          onPress={() => runBot('kart')}
          disabled={running !== null || status === 'offline'}
        >
          <View style={styles.cardHeader}>
            <Activity color="#60a5fa" size={24} />
            <Text style={styles.cardTitle}>Kart / Korner</Text>
          </View>
          <Text style={styles.cardDesc}>İstatistik scriptini internet üzerinden çalıştırarak kart ve korner verilerini günceller.</Text>
          <View style={[styles.button, { backgroundColor: '#1d4ed8' }]}>
            {running === 'kart' ? (
              <ActivityIndicator color="white" />
            ) : (
              <>
                <Play color="white" size={18} fill="white" />
                <Text style={styles.buttonText}>ANALİZİ BAŞLAT</Text>
              </>
            )}
          </View>
        </TouchableOpacity>

        <View style={styles.console}>
          <View style={styles.consoleHeader}>
            <Terminal color="#94a3b8" size={14} />
            <Text style={styles.consoleHeaderText}>SİSTEM LOGLARI</Text>
          </View>
          {logs.map((log, i) => (
            <Text key={i} style={styles.logText}>{log}</Text>
          ))}
          <Text style={styles.infoText}>* Tünel Şifresi Gerekebilir: 176.41.51.55</Text>
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
  statusSection: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
    backgroundColor: '#061614',
    padding: 8,
    borderRadius: 20,
    alignSelf: 'center',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  statusText: {
    color: '#f8fafc',
    fontSize: 10,
    fontWeight: 'bold',
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
  },
  infoText: {
    color: '#475569',
    fontSize: 10,
    marginTop: 10,
    fontStyle: 'italic'
  }
});
