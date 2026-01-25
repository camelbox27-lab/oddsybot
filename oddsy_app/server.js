const express = require('express');
const { spawn } = require('child_process');
const cors = require('cors');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

// Relative paths for Cloud/Docker environment
// server.js is in /oddsy_app, so we go up one level for root
const BOT_PATH = path.join(__dirname, '..');
const ISTATISTIK_PATH = path.join(__dirname, '../istatistik');

const runScript = (scriptName, cwd, res) => {
    console.log(`Executing ${scriptName} in ${cwd}`);

    // 'python' is usually correct for Docker images based on python
    // If using a specific python version alias, it might need adjustment (e.g. python3)
    const pythonProcess = spawn('python', [scriptName], {
        cwd,
        env: { ...process.env, PYTHONUNBUFFERED: '1', PYTHONIOENCODING: 'utf-8' }
    });

    let output = '';
    let error = '';

    pythonProcess.stdout.on('data', (data) => {
        const str = data.toString();
        output += str;
        console.log(str);
    });

    pythonProcess.stderr.on('data', (data) => {
        const str = data.toString();
        error += str;
        console.error(str);
    });

    pythonProcess.on('close', (code) => {
        if (code === 0) {
            res.json({ success: true, message: 'Script completed successfully', output });
        } else {
            res.status(500).json({ success: false, message: 'Script failed', error, code });
        }
    });

    // Timeout after 10 minutes (scraping can be slow)
    setTimeout(() => {
        if (!pythonProcess.killed) pythonProcess.kill();
    }, 600000);
};

app.post('/api/run-oran', (req, res) => {
    runScript('main.py', BOT_PATH, res);
});

app.post('/api/run-kart-korner', (req, res) => {
    runScript('main.py', ISTATISTIK_PATH, res);
});

app.get('/api/status', (req, res) => {
    res.json({ status: 'online' });
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Oddsy Cloud Server running on port ${PORT}`);
});
