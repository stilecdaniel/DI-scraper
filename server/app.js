const express = require('express');
const fetchRepoData = require('./utils/fetchRepoData.js');
const parseCSV = require('./utils/parseCSV.js');

const app = express();

const port = process.env.PORT || 8080;

app.use(express.json());

app.get('/', async (req, res) => {

    try {
        const scraperDataObject = await fetchRepoData();
        const parsedScraperData = await parseCSV(scraperDataObject.content);
        console.log(parsedScraperData);
    } catch (e) {
        res.status(500).send("Error getting csv data: " + e);
    }
})

app.listen(port, () => {
    console.log(`\nServer is running on http://localhost:${port}`);
});