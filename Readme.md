# easee-tibber
Python script for sending current tibber electricity price to easee wallbox charger.


## Installation

First clone this repository, and setup your config.json file.

```
git clone git@github.com:andreaseu/easee-tibber.git
cp config.example config.json
```

Login to Easee Cloud to access the bearer token

```

https://easee.cloud/external/login-devportal?redirect=%2Freference%2Fpost_api-accounts-login
```

Run the set_price.py file manually.

```
python3 set_price.py
```

Or create a cron job on Linux Server to start price matching every hour at 5 minutes past the hour.

````
5 * * * /usr/bin/python3 /opt/script/tibber-easee/set_price.py
```