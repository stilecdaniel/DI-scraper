# Express.js server

The server has 6 endpoints, 3 of them will return current program info data for each channel,
and the other 3 return the viewership for the program

## Base server URL: http://63.179.147.89:3000

## Program data endpoints:
- /dajto
- /prima-sk
- /markiza-krimi

## Program viewership endpoints:
- /dajto/viewership
- /prima-sk/viewership
- /markiza-krimi/viewership

Upon making a request, the server uses SSE (server side events) to stream json
strings in an interval of 5 minutes. These strings contain information about 
the currently played show on the channel.

### Example output string:
{"channel":"dajto","date":"2025-10-08","start":"20:30","title":"Noc pomsty","rating":"93%","year":"2017","season":"","episode":"","startDate":"2025-10-08T18:30:00.000Z"}

## Installation
- npm install