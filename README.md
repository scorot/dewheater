# dewheater

A dewheater service for my allsky camera.

# Prerequisite

This setup instructions assumes that your are using the allsky camera from [AllSkyTeam](https://github.com/AllskyTeam/allsky). Therefore you should have an allsky directory in the home directory of your pi.

# Preparation
Move into the allsky directory and clone this github repository:

```shell
cd allsky
git clone https://github.com/scorot/dewheater.git
```

Now prepare a python virtual env:

```shell
cd dewhearter
python3 -m venv ./venv
./venv/bin/activate
```

An install the python packages required:

```shell
pip3 install pyowm adafruit-circuitpython-dht
```
Once the download finished, you can deactivate the environnement by simply typing ``deactivate``.

# Configuration

Copy the provided ``settings_dewheater.json.repo`` file into ``settings_dewheater.json``:

```shell
cp settings_dewheater.json.repo settings_dewheater.json
```

Now edit the file accorind to you needs. The most important settings are the relay pin number and the OpenWeatherMap API key. Without these two, the service won't run.

# Service activation

Run the install script provided as follown:

```shell
sudo ./install.sh
```

Once the install script finished you can check if the service is running with the command ``sudo systemctl status dewheater`` which should output something as bellow:

```
pi@allsky:~/allsky/dewheater $ sudo systemctl status dewheater
● dewheater.service - Dew Heater for All Sky Camera
     Loaded: loaded (/lib/systemd/system/dewheater.service; disabled; preset: enabled)
     Active: active (running) since Mon 2024-05-06 11:53:26 CEST; 8s ago
   Main PID: 9685 (python3)
      Tasks: 1 (limit: 1569)
        CPU: 2.980s
     CGroup: /system.slice/dewheater.service
             └─9685 /home/pi/allsky/dewheater/venv/bin/python3 /home/pi/allsky/dewheater/dewheater.py

mai 06 11:53:28 allsky python3[9685]: /home/pi/allsky/config
mai 06 11:53:28 allsky python3[9685]: Read /home/pi/allsky/config/settings_RPi_HQ.json
mai 06 11:53:28 allsky python3[9685]: Read /home/pi/allsky/dewheater/settings_dewheater.json
mai 06 11:53:28 allsky python3[9685]: Camera location is 48.056N 7.42E
mai 06 11:53:28 allsky python3[9685]: loop sleep time is 300s
mai 06 11:53:28 allsky python3[9685]: Start relay test...
mai 06 11:53:30 allsky python3[9685]: Test succeded.
mai 06 11:53:30 allsky python3[9685]: Start dew heater service...
mai 06 11:53:31 allsky python3[9685]: Internal temperature = 28.6 > 10.48 + 8.5
mai 06 11:53:31 allsky python3[9685]: Sleep for 300 seconds...
```

