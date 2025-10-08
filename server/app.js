const express = require('express');
const fetchRepoData = require('./utils/fetchRepoData.js');
const parseCSV = require('./utils/parseCSV.js');
const getCurrentlyPlayingShow = require('./utils/getCurrentlyPlayingShow');

const app = express();
const port = process.env.PORT || 8080;

app.use((req, res, next) => {
    res.set({
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
    });
    res.flushHeaders();
    next();
});

let channelData = {};

async function initializeData() {
    try {
        const scraperDataObject = await fetchRepoData();
        const parsedData = await parseCSV(scraperDataObject.content);
        const todayString = new Date().toISOString().slice(0, 10);

        const todayData = parsedData.filter(show => show.date === todayString);

        channelData = {
            dajto: todayData.filter(show => show.channel === "dajto"),
            'markiza-krimi': todayData.filter(show => show.channel === "markiza-krimi"),
            'prima-sk': todayData.filter(show => show.channel === "prima-sk")
        };
    } catch (error) {
        console.error("Failed to initialize show data:", error);
    }
}

function streamData(getDataFn, res) {
    const intervalId = setInterval(() => {
        const data = getDataFn();
        res.write(data + "\n\n");
    }, 5 * 60 * 1000);

    res.on('close', () => {
        clearInterval(intervalId);
        res.end();
    });
}

function createChannelStreamHandler(channel) {
    return (req, res) => {
        if (!channelData[channel]) {
            res.status(503).send("Data not initialized");
            return;
        }

        streamData(() => getCurrentlyPlayingShow(channelData[channel]), res);
    };
}

app.get('/dajto/', createChannelStreamHandler('dajto'));
app.get('/prima-sk/', createChannelStreamHandler('prima-sk'));
app.get('/markiza-krimi/', createChannelStreamHandler('markiza-krimi'));

app.use((req, res, next) => {
    res.status(404).write('Not found');
});

app.listen(port, async () => {
    const initRetryTimes = 5;

    for (let i = 0; i < initRetryTimes; i++) {
        try {
            await initializeData();
            console.log(`Server is running on http://localhost:${port}`);
            break;
        } catch (e) {
            console.error("Failed to initialize data, attempt: " + (i + 1) + "error: " + e);
            if (i === initRetryTimes - 1) {
                console.error("Cant initialize server data, shutting down");
                process.exit(1);
            }
        }
    }
});