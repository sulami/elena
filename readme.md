# Elena

A dynamic status API

### Features

Elena is a lightweight API that provides access to user-defined stati in JSON
form. You can push status updates to Elena or configure it to pull for updates
after a set delay. It also provides access to the history of a given status, if
needed.

### Setup

To run Elena, you will need Python and Flask, most somewhat recent versions
will do. Just start up `run.py` and you should be good to go. Edit `config.py`
to enter your database details.

### Usage

To add a new status to the system, send a POST request to
`your.server/set/statusname`, adding the value to return later on in the POST
dictionary as `value`.

    curl --data "value=True" http://example.com/set/online/

This will set the "online" status to true. Test this by requesting
`your.server/get/statusname`.

    curl http://example.com/get/online

This should return the status and HTTP code 200. In case anything goes wrong,
Elena will return a non-success HTTP code and an error message starting with
"ERROR: ", so you can automate checking for errors easily. Successful requests
that do not return a status return "Success!" in the HTTP body, as well as a
20X HTTP code.

You can change a status attribute by requesting `your.server/atr/statusname`,
attaching the attributes to change in the POST dictionary like this:

    curl --data "history=true&pull=true&pull_url=example.com/api/online&pull_time=300" http://example.com/atr/online

This will enable history logging for the online stat as well as switching it
from push to pull, which means that if you request the status and it is older
than 5 minutes (300 seconds), it will check the `pull_url` and try to parse the
response. You can still push update for this status via `.../set/online`.

If you want to check the history of a status, you can access
`your.server/hist/statusname` to get all recorded status updates with
timestamps to work with.

