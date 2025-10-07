const csv = require('csvtojson');

/**
 * Parses the base64 encoded csv data to an array of objects
 * @async
 * @param data base64 string of csv file
 * @returns {Converter}
 */
async function parseCSV(data) {
    const csvData = Buffer.from(data, "base64").toString("utf8");

    return csv().fromString(csvData);
}

module.exports = parseCSV;