# Express.js server

The server has 12 endpoints in 2 groups, in each group 3 of them will return current program info data for each channel,
and the other 3 return the viewership for the program. The route /pull at the end specifies if the response should be
a continuous SSE stream or a one time response

## Base server URL: http://63.179.147.89:3000

## Program data endpoints:
- /dajto
- /prima-sk
- /markiza-krimi

## Program viewership endpoints:
- /dajto/viewership
- /prima-sk/viewership
- /markiza-krimi/viewership

### Every endpoint has an additional route "/pull", so that only one json response will be returned
- /dajto/pull
- /dajto/viewership/pull
- /prima-sk/viewership/pull

etc...

Upon making a request, the server uses SSE (server side events) to stream json
strings in an interval of 5 minutes, or sends a single json response based on if the route /pull
is requested. These responses contain information about 
the currently played show on the channel, or its viewership.

### Example output strings:
- {"channel":"dajto","date":"2025-10-08","start":"20:30","title":"Noc pomsty","rating":"93%","year":"2017","season":"","episode":"","startDate":"2025-10-08T18:30:00.000Z"}
- {"viewership":97811}

## Installation
- npm install