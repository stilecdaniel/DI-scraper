# Express.js server

The server has 3 endpoints, one for each channel:
- url-placeholder/dajto
- url-placeholder/markiza-krimi
- url-placeholder/prima-sk

Upon making a request, the server uses SSE (server side events) to stream json
strings in an interval of 5 minutes. These strings contain information about 
the currently played show on the channel.

### Example output string:
{"channel":"dajto","date":"2025-10-08","start":"20:30","title":"Noc pomsty","rating":"93%","year":"2017","season":"","episode":"","startDate":"2025-10-08T18:30:00.000Z"}

## Installation
- npm install