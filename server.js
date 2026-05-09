const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');

const app = express();
const PORT = 8000;

app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
    res.json({ message: 'Twitter Sentiment Analysis API (Node.js + Python ML)' });
});

app.post('/predict', (req, res) => {
    const tweet = req.body.tweet;
    
    if (!tweet) {
        return res.status(400).json({ error: 'No tweet provided' });
    }

    // Spawn Python process
    const pythonProcess = spawn('python', ['predict.py', tweet]);
    
    let resultData = '';
    let errorData = '';

    // Collect data from standard output
    pythonProcess.stdout.on('data', (data) => {
        resultData += data.toString();
    });

    // Collect data from standard error (in case of exceptions)
    pythonProcess.stderr.on('data', (data) => {
        errorData += data.toString();
    });

    // When the process closes
    pythonProcess.on('close', (code) => {
        if (code !== 0 || errorData) {
            console.error('Python Script Error:', errorData);
            // We only return 500 if resultData couldn't be parsed as JSON fallback
        }
        
        try {
            // Parse the JSON string from stdout
            const jsonResponse = JSON.parse(resultData.trim());
            if (jsonResponse.error) {
                return res.status(500).json({ error: jsonResponse.error });
            }
            res.json(jsonResponse);
        } catch (e) {
            console.error('JSON Parse Error:', e);
            console.error('Raw Output:', resultData);
            res.status(500).json({ error: 'Failed to process the prediction' });
        }
    });
});

app.listen(PORT, () => {
    console.log(`Node.js server running on http://localhost:${PORT}`);
});
