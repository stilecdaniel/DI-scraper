const express = require('express');
const fetchRepoData = require('./utils/fetchRepoData.js');
const parseCSV = require('./utils/parseCSV.js');

const app = express();
const port = process.env.PORT || 8080;

app.use((req, res, next) => {
    res.set({
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
    });
    next();
});

let initData;

async function initializeData() {
    try {
        const scraperDataObject = await fetchRepoData();
        initData = await parseCSV(scraperDataObject.content);
    } catch (e) {
        console.error("Failed to initialize show data: " + e);
    }
}

function streamData(res) {
    setInterval(() => {
        res.write("data: test\n\n");
    }, 1000);
}

app.get('/dajto', (req, res) => {

    if (!initData) {
        res.status(503).send("Data not initialized on server");
        return;
    }
    streamData(res);
})

app.get('/prima-sk', (req, res) => {

    if (!initData) {
        res.status(503).send("Data not initialized on server");
        return;
    }
    streamData(res);
})

app.get('/markiza-krimi', (req, res) => {

    if (!initData()) {
        res.status(503).send("Data not initialized on server");
        return;
    }
    streamData(res);
})

app.listen(port, async () => {
    await initializeData();
    console.log(`\nServer is running on http://localhost:${port}`);
});