const express = require('express');
const fetchRepoData = require('./utils/fetchRepoData.js');
const parseCSV = require('./utils/parseCSV.js');
const getCurrentlyPlayingShow = require('./utils/getCurrentlyPlayingShow');
const generateViewership = require('./utils/generateViewership');

const app = express();
const port = process.env.PORT || 3000;

let channelData = {};
const interval = 5 * 60 * 1000;

/**
 * Initializes the three stations data into an object with three properties, one for each channel
 * @returns {Promise<void>} The stations data promise
 */
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

/**
 * Sends the chosen data to the client in an interval
 * @param getDataFn function that returns the chosen data to write to the client in the format that should be sent
 * @param res
 */
function streamData(getDataFn, res) {
    const data = getDataFn();
    res.write("data: " + data + "\n\n");

    const intervalId = setInterval(() => {
        const data = getDataFn();
        res.write("data: " + data + "\n\n");
    }, interval);

    res.on('close', () => {
        clearInterval(intervalId);
        res.end();
    });
}

/**
 * Handles the data streaming, what channel should be streamed or if viewership should be streamed instead
 * @param channel Which channels currently playing program should be streamed, if showViewership is true, this argument is disregarded
 * @param showViewership If set to true, it will not stream the currently playing program but the viewership
 * @returns {(function(*, *): void)|*}
 */
function createChannelStreamHandler(channel, showViewership) {
    return (req, res) => {
        res.set({
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        });
        res.flushHeaders();

        if (!showViewership) {
            if (!channelData[channel]) {
                res.status(503).send("Data not initialized");
                return;
            }
            streamData(() => (getCurrentlyPlayingShow(channelData[channel])), res);
        } else {
            streamData(() => (generateViewership(channelData, channel)), res);
        }
    }
}

function getChannelCurrentData(channel, showViewership) {
    return (req, res) => {
        res.set({
            'Content-Type': 'application/json',
        });

        if (!showViewership) {
            if (!channelData[channel]) {
                res.status(503).send("Data not initialized");
                return;
            }
            res.status(200).json(getCurrentlyPlayingShow(channelData[channel]));
        } else {
            res.status(200).json(generateViewership(channelData, channel));
        }
    }
}

/**
 * These endpoints send SSE (Server side events) periodically
 */
app.get('/dajto/', createChannelStreamHandler('dajto', false));
app.get('/prima-sk/', createChannelStreamHandler('prima-sk', false));
app.get('/markiza-krimi/', createChannelStreamHandler('markiza-krimi', false));

app.get('/dajto/viewership/', createChannelStreamHandler('dajto', true));
app.get('/prima-sk/viewership/', createChannelStreamHandler('prima-sk', true));
app.get('/markiza-krimi/viewership/', createChannelStreamHandler('markiza-krimi', true));

/**
 * These endpoints return a single response of the currently playing show or its viewership
 */
app.get('/dajto/pull', getChannelCurrentData('dajto', false));
app.get('/prima-sk/pull', getChannelCurrentData('prima-sk', false));
app.get('/markiza-krimi/pull', getChannelCurrentData('markiza-krimi', false));

app.get('/dajto/viewership/pull', getChannelCurrentData('dajto', true));
app.get('/prima-sk/viewership/pull', getChannelCurrentData('prima-sk', true));
app.get('/markiza-krimi/viewership/pull', getChannelCurrentData('markiza-krimi', true));


app.use((req, res, next) => {
    res.status(404).write('Not found');
});

app.listen(port, '0.0.0.0', async () => {
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
