/**
 * Function will return the currently playing program based
 * on the program objects start time
 * @param programs an array of program objects of the channel
 * @returns {string} JSON.stringified program object
 */
function getCurrentlyPlayingShow(programs) {

    const currentDate = new Date();

    programs.forEach(program => {
        program.startDate = new Date(`${program.date}T${program.start}:00`);
    });

    let currentProgram = null;
    let closestTimeDiff = Infinity;

    programs.forEach(program => {
        const startTime = program.startDate.getTime();
        const now = currentDate.getTime();

        if (startTime <= now) {
            const diff = now - startTime;
            if (diff < closestTimeDiff) {
                closestTimeDiff = diff;
                currentProgram = program;
            }
        }
    });

    return JSON.stringify(currentProgram);
}

module.exports = getCurrentlyPlayingShow;