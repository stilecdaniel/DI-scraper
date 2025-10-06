/**
 * Fetches the csv file data from our Repository.
 * @async
 * @returns {Promise<Object>} the GitHub API returns a json object with base64 encoded csv data.
 * @throws {Error} If the fetch request to the repo fails.
 */
async function fetchRepoData() {

    const showsRepoUrl = "https://api.github.com/repos/stilecdaniel/DI-scraper/contents/shows.csv";

    try {
        const response = await fetch(showsRepoUrl);
        return await response.json();
    } catch (e) {
        console.error("Error retrieving csv file: " + e);
        throw e;
    }
}

module.exports = fetchRepoData;
