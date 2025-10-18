const getCurrentlyPlayingShow = require('./getCurrentlyPlayingShow');

const lastViewershipByChannel = {}

/**
 * Generates viewership for each channel's currently running program.
 * It stores the running programs title and viewership, and if the program
 * is still running, generates a new viewership with a 0.5% deviation from
 * the original viewership
 * @param channelData
 * @param channel
 * @returns {string}
 */
function generateViewership(channelData, channel) {
    const currentShow = JSON.parse(getCurrentlyPlayingShow(channelData[channel]));

    const currentShowTitle = currentShow.title;

    if (!lastViewershipByChannel[channel]) {
        lastViewershipByChannel[channel] = {
            lastShowTitle: currentShowTitle,
            lastViewershipCount: Math.floor(Math.random() * (100000 - 500 + 1)) + 500
        };

        return JSON.stringify({viewership: lastViewershipByChannel[channel].lastViewershipCount});
    }

    const viewershipInfo = lastViewershipByChannel[channel];
    let newViewershipCount;

    if (currentShowTitle === viewershipInfo.lastShowTitle) {
        const variation = viewershipInfo.lastViewershipCount * 0.005;
        const min = Math.ceil(Math.max(viewershipInfo.lastViewershipCount - variation, 500));
        const max = Math.floor(Math.min(viewershipInfo.lastViewershipCount + variation, 100000));
        newViewershipCount = Math.floor(Math.random() * (max - min + 1)) + min;
        lastViewershipByChannel[channel].lastViewershipCount = newViewershipCount;
    } else {
        newViewershipCount = Math.floor(Math.random() * (100000 - 500 + 1)) + 500;
        lastViewershipByChannel[channel].lastShowTitle = currentShowTitle;
        lastViewershipByChannel[channel].lastViewershipCount = newViewershipCount;
    }

    return JSON.stringify({viewership: newViewershipCount});
}

module.exports = generateViewership;