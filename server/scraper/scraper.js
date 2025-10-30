const cheerio = require('cheerio');
const {format, addDays} = require('date-fns');

async function fetchHtml(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Failed to fetch ${url}: ${response.statusText}`);
    }
    return await response.text();
}

/**
 * Scrapes the channel data from https://tv-program.sk/${channelName}/
 * and returns the object that contains the weeks program data
 * @param url
 * @returns {Promise<*[]>}
 */
async function scrapeSingleUrl(url) {
    const html = await fetchHtml(url);
    const $ = cheerio.load(html);

    const dayColumns = $('div.programme-list.bg-light.h-100.d-flex.flex-column.den');

    const detailPromises = [];

    dayColumns.each((colIndex, colElem) => {
        const currentDate = addDays(new Date(), colIndex);
        const dateString = format(currentDate, 'yyyy-MM-dd');

        const timeElements = $(colElem).find('time.programme-list__time').toArray();
        const progNames = $(colElem).find('a.programme-list__title').toArray();

        for (let i = 0; i < progNames.length; i++) {
            const prog = progNames[i];
            const time = timeElements[i];
            const showHref = $(prog).attr('href');
            const detailUrl = 'https://tv-program.sk' + showHref;

            detailPromises.push(
                scrapeShowDetails(detailUrl, dateString, $(time).text().trim(), $(prog).text().trim(), url)
            );
        }
    });

    return await Promise.all(detailPromises);
}

/**
 * Helper function to scrape the details for each program item in the column
 * @param detailUrl url of the program to scrape
 * @param dateString date of the program
 * @param startTime start time of the program
 * @param title programs title
 * @param channelUrl channel of the program
 * @returns {Promise<{channel: unknown, date: *, start: *, title: *, rating: null, year: null, season: null, episode: null}>}
 */
async function scrapeShowDetails(detailUrl, dateString, startTime, title, channelUrl) {
    const detailHtml = await fetchHtml(detailUrl);
    const $$ = cheerio.load(detailHtml);

    const showInfo = $$('div.adspace-program-detail');

    let year = null;
    showInfo.find('span.text-muted').each((_, el) => {
        const text = $$(el).text().trim();
        if (/^\d{4}$/.test(text)) {
            year = text;
        }
    });

    let season = null;
    let episode = null;
    const pageTitleContainer = $$('h1.page__title');
    if (pageTitleContainer.length) {
        const heading = pageTitleContainer.find('span.text-muted.fs-medium');
        if (heading.length) {
            const seasonEpisodeStr = heading.text().trim();
            const mainString = seasonEpisodeStr.split('-')[0].trim();
            const parts = mainString.split('/').map(p => p.trim());
            if (parts.length >= 2) {
                season = parts[0];
                episode = parts[1];
            }
        }
    }

    let ratingPercentage = null;
    const showRatingContainer = $$('div.text-center.bg-warning.mx-n3.mx-lg-n4.px-3.px-lg-4.py-3');
    if (showRatingContainer.length) {
        const ratingPercentageContainer = showRatingContainer.find('div.h3.mb-0');
        if (ratingPercentageContainer.length) {
            ratingPercentage = ratingPercentageContainer.text().trim();
        }
    }

    return {
        channel: channelUrl.replace(/\/$/, '').split('/').pop(),
        date: dateString,
        start: startTime,
        title: title,
        rating: ratingPercentage,
        year: year,
        season: season,
        episode: episode,
    };
}

module.exports = scrapeSingleUrl;