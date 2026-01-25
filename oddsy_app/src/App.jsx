import React, { useState, useEffect } from 'react';
import { Play, BarChart2, Activity, Terminal, RefreshCw } from 'lucide-react';

const App = () => {
    const [running, setRunning] = useState(null);
    const [logs, setLogs] = useState(['ODDSY Mobile Console Ready.']);
    const [status, setStatus] = useState('checking');

    useEffect(() => {
        const check = async () => {
            try {
                const res = await fetch('http://localhost:3001/api/status');
                if (res.ok) setStatus('online');
                else setStatus('offline');
            } catch { setStatus('offline'); }
        };
        check();
        const inv = setInterval(check, 5000);
        return () => clearInterval(inv);
    }, []);

    const addLog = (m) => setLogs(p => [...p.slice(-3), `> ${m}`]);

    const run = async (t) => {
        if (running || status === 'offline') return;
        setRunning(t);
        addLog(`Başlatılıyor: ${t === 'oran' ? 'Oran Analiz' : 'Kart/Korner Analiz'}...`);
        try {
            const res = await fetch(`http://localhost:3001/api/run-${t === 'oran' ? 'oran' : 'kart-korner'}`, { method: 'POST' });
            const data = await res.json();
            if (data.success) addLog(`${t} tamamlandı.`);
            else addLog(`HATA: ${data.message}`);
        } catch { addLog('Bağlantı hatası!'); }
        finally { setRunning(null); }
    };

    return (
        <div className="mobile-container">
            <div className="header">
                <div className="logo">ODDSY</div>
                <div className="subtitle">MOBİL KONTROL MERKEZİ</div>
            </div>

            <div className="button-group">
                <div className="action-card" onClick={() => run('oran')}>
                    <div className="card-title">Oran Analiz</div>
                    <div className="card-desc">Python botunu çalıştırarak güncel oran analizlerini başlatır.</div>
                    <button className="card-button" disabled={running !== null || status === 'offline'}>
                        {running === 'oran' ? <RefreshCw className="running" size={18} /> : <Play size={18} />}
                        {running === 'oran' ? 'ÇALIŞIYOR...' : 'ANALİZ BAŞLAT'}
                    </button>
                </div>

                <div className="action-card" onClick={() => run('kart')}>
                    <div className="card-title">Kart / Korner</div>
                    <div className="card-desc">İstatistik scriptini çalıştırarak kart ve korner verilerini günceller.</div>
                    <button className="card-button secondary" disabled={running !== null || status === 'offline'}>
                        {running === 'kart' ? <RefreshCw className="running" size={18} /> : <Play size={18} />}
                        {running === 'kart' ? 'ÇALIŞIYOR...' : 'ANALİZ BAŞLAT'}
                    </button>
                </div>

                <div className="console">
                    <div style={{ marginBottom: 5, fontSize: 10, display: 'flex', justifyContent: 'space-between' }}>
                        <span><Terminal size={12} style={{ verticalAlign: 'middle' }} /> LOGLAR</span>
                        <span><span className={`status-dot ${status}`} /> {status.toUpperCase()}</span>
                    </div>
                    {logs.map((l, i) => <div key={i}>{l}</div>)}
                </div>
            </div>
        </div>
    );
};

export default App;
