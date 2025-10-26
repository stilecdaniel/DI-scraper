const cheerio = require('cheerio');

/**
 * Scrapes the channel data from https://tv-program.sk/${channelName}/
 * and returns the object that contains the data
 * @param url
 * @returns {Promise<*[]>}
 */
async function scrapeSingleUrl(url) {
    const collectedShows = [];

    const response = await fetch(url);
    const html = await response.text();
    const $ = cheerio.load(html);

    const programmeList = $('.programme-list');

    const times = programmeList.find('time.programme-list__time').toArray();
    const progNames = programmeList.find('a.programme-list__title').toArray();

    for (let i = 0; i < progNames.length; i++) {
        const progElement = progNames[i];
        const timeElement = times[i];

        const title = $(progElement).text().trim();
        const start = $(timeElement).text().trim();
        const href = 'https://tv-program.sk' + $(progElement).attr('href');

        const detailResponse = await fetch(href);
        const detailHtml = await detailResponse.text();
        const detailPage = cheerio.load(detailHtml);

        const showInfo = detailPage('div.adspace-program-detail');

        let year = null;
        showInfo.find('span.text-muted').each((_idx, elem) => {
            const text = detailPage(elem).text().trim();
            if (/^\d{4}$/.test(text)) {
                year = text;
            }
        });

        let season = null;
        let episode = null;
        const pageTitleContainer = detailPage('h1.page__title');
        if (pageTitleContainer.length) {
            const heading = pageTitleContainer.find('span.text-muted.fs-medium');
            if (heading.length) {
                const seasonEpisode = heading.text().trim();
                const mainString = seasonEpisode.split('-')[0].trim();
                const parts = mainString.split('/').map(part => part.trim());
                season = parts[0];
                episode = parts[1];
            }
        }

        let rating = null;
        const showRatingContainer = detailPage('div.text-center.bg-warning.mx-n3.mx-lg-n4.px-3.px-lg-4.py-3');
        if (showRatingContainer.length) {
            const ratingPercentageContainer = showRatingContainer.find('div.h3.mb-0');
            if (ratingPercentageContainer.length) {
                rating = ratingPercentageContainer.text().trim();
            }
        }

        collectedShows.push({
            channel: url.replace(/\/$/, '').split('/').pop(),
            date: new Date().toISOString().split('T')[0],
            start,
            title,
            rating,
            year,
            season,
            episode
        });
    }
    return collectedShows;
}

module.exports = scrapeSingleUrl;