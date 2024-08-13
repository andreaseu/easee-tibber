# easee-tibber
Python script for sending current tibber electricity price to easee wallbox charger.


## Installation

First clone this repository, and setup your config.json file.

```

-- Create a docker base folder

mkdir /home/loginuser/scripts/
git clone git@github.com:andreaseu/easee-tibber.git /home/loginuser/scripts/easee-tibber
mkdir /home/loginuser/scripts/easee-tibber/logs
sudo ln -s /home/loginuser/scripts/ /opt/scripts


cd /opt/scripts/easee-tibber

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
5 * * * * /usr/bin/python3 /opt/scripts/easee-tibber/set_price.py >> /opt/scripts/easee-tibber/logs/setprice.log 2>&1
```
