#!/usr/bin/python3

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import adafruit_dht
from datetime import datetime
from math import log

import RPi.GPIO as GPIO

import pyowm
import json
import logging
import os


def get_config(allsky_conf_file, dewheater_conf_file):
    """Read allsky json config file to get the location
    and also read the dew heater json config file.

    Returns a dictionnary with all the configuration 
    parameters.
    """
    if os.path.exists("/etc/raspap/" + allsky_conf_file):
        print("Read {}".format("/etc/raspap/" + allsky_conf_file))
        with open("/etc/raspap/" + allsky_conf_file, 'r') as fc:
            j = json.load(fc)
    elif os.path.exists("/home/pi/allsky/" + allsky_conf_file):
        print("Read {}".format("/home/pi/allsky/" + allsky_conf_file))
        with open("/home/pi/allsky/" + allsky_conf_file, 'r') as fc:
            j = json.load(fc)
    else:
        raise IOError("allsky config file not found")

    if os.path.exists("/etc/raspap/" + dewheater_conf_file):
        print("Read {}".format("/etc/raspap/" + dewheater_conf_file))
        with open("/etc/raspap/" + dewheater_conf_file, 'r') as fc:
            j.update(json.load(fc))
    elif os.path.exists("/home/pi/allsky/dewheater/" + dewheater_conf_file):
        print("Read {}".format("/home/pi/allsky/dewheater/" + dewheater_conf_file))
        with open("/home/pi/allsky/dewheater/" + dewheater_conf_file, 'r') as fc:
            j.update(json.load(fc))
    else:
        raise IOError("dewheater config file not found")

    print("Camera location is {} {}".format(j.get('latitude'),
                                            j.get('longitude')))
    latitude = j.get('latitude')
    if 'N' in latitude:
        latitude = float(j.get('latitude').replace('N',''))
    elif 'S' in latitude:
        latitude = -1. * float(j.get('latitude').replace('S',''))
    else:
        pass

    longitude = j.get('longitude')
    if 'E' in longitude:
        longitude = float(j.get('longitude').replace('E',''))
    elif 'W' in longitude:
        longitude = -1. * float(j.get('longitude').replace('W',''))
    else:
        pass
    j.update({ 'latitude' : latitude, 'longitude' : longitude })
    print("loop sleep time is {}s".format(j.get("loop_sleep_time")))
    return j


def dew_point(temp, rh):
    """Compute dew point temperature from temperature
    and relative humidity percentage.
    """
    b = 18.678
    c = 257.14
    gamma = log(rh/100.) + ( b * temp / (c + temp))
    temp_dp = (c * gamma) / (b - gamma) 

    return temp_dp


def get_owm_ext_data(api_key, lat, longi):
    """Get outdoor temperature en relative humidity from
    OpemWeaterhMap.
    """
    owm = pyowm.OWM(api_key)
    mgr = owm.weather_manager()
    obs = mgr.weather_at_coords(lat, longi)
    temp = obs.weather.temperature('celsius').get('temp')
    humidity = obs.weather.humidity

    return temp, humidity


def set_heater_on(pin, status):
    """Activate the heater relay.
    """
    if status == False:
        GPIO.output(pin, True)
        #now = datetime.now()
        #current_time = now.strftime("%d/%m/%Y-%H:%M:%S")
        print("Turn on heater")
        return True
    else:
        #print("Heater allready on. Keep it on")
        return status


def set_heater_off(pin, status):
    """De-activate the heater relay.
    """
    if status == True:
        GPIO.output(pin, False)
        #now = datetime.now()
        #current_time = now.strftime("%d/%m/%Y-%H:%M:%S")
        print("Turn off heater")
        return False 
    else:
        #print("Heater allready off. Keep it off")
        return status

def get_board_from_pin(pin):
    """Translate pin number given as interget in the
    json file into a adafruit board class object.
    """
    if pin ==  board.D2.id:
        return board.D2
    if pin == board.D3.id:
        return board.D3
    if pin == board.D4.id:
        return board.D4
    if pin == board.D5.id:
        return board.D5
    if pin == board.D6.id:
        return board.D6
    if pin == board.D14.id:
        return board.D14
    if pin == board.D15.id:
        return board.D15
    if pin == board.D16.id:
        return board.D16
    if pin == board.D17.id:
        return board.D17
    if pin == board.D18.id:
        return board.D18
    #return board.D4
    return 0


#if __name__ == '__main__':
def main(config):

    # log file where all the data collected will stored
    datalogger = '/var/log/dewheater_data.log'
    logging.basicConfig(filename=datalogger,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.INFO)

    relaypin = conf.get("relay_board_pin")
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    #GPIO.setmode(GPIO.BOARD)
    GPIO.setup(relaypin, GPIO.OUT)

    dht22_board_pin = get_board_from_pin(conf.get("dht22_board_pin"))
    # Initial the dht device, with data pin connected to:
    #dhtDevice = adafruit_dht.DHT22(board.D4)

    # you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
    # This may be necessary on a Linux single board computer like the Raspberry Pi,
    # but it will not work in CircuitPython.
    #dhtDevice = adafruit_dht.DHT22(conf.get("dht22_board_pin"), use_pulseio=False)
    dhtDevice = adafruit_dht.DHT22(dht22_board_pin, use_pulseio=False)
    #dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)

    # a simple relay test before starting
    try:
        print("Start relay test...")
        GPIO.output(relaypin, True)
        time.sleep(1.0)
        GPIO.output(relaypin, False)
        time.sleep(1.0)
        print("Test succeded.")
    except Exception:
        print("Test relay failed.")

    print("Start dew heater service...")

    heater_status = False
    status = True
    try: 
        while True:
            try:
                # Print the values to the serial port
                temp_in = dhtDevice.temperature
                humidity_in = dhtDevice.humidity
                dewpoint_in = dew_point(temp_in, humidity_in)

                temp_ext, humidity_ext = get_owm_ext_data(conf.get("owm_api_key"),
                        conf.get("latitude"), conf.get("longitude"))
                dewpoint_ext = dew_point(temp_ext, humidity_ext)

                tdiff = conf.get("dew_temp_correction")
                if temp_in < dewpoint_ext + tdiff:
                    #print("Internal temperature = {} < {:1.2f} + {} ".format(temp_in, dewpoint_ext, tdiff))
                    heater_status = set_heater_on(relaypin, heater_status)

                if temp_in > dewpoint_ext + tdiff + 0.5:
                    #print("Internal temperature = {} > {:1.2f} + {}".format(temp_in, dewpoint_ext, tdiff+0.5))
                    heater_status = set_heater_off(relaypin, heater_status)
                #print('{} {} {} {}'.format(temp_in, dewpoint_in, temp_ext, dewpoint_ext))
                logging.info('{} {:1.2f} {} {} {:1.2f} {} {}'.format(temp_in, dewpoint_in, humidity_in,
                                                               temp_ext, dewpoint_ext, humidity_ext,
                                                               heater_status))

            except RuntimeError as error:
                # Errors happen fairly often, DHT's are hard to read, just keep going
                #print(error.args[0])
                time.sleep(5.0)
                continue
            except Exception as error:
                dhtDevice.exit()
                GPIO.cleanup()
                print("An error occured. Exiting...")
                exit(1)
                #raise error

            time.sleep(conf.get("loop_sleep_time"))
            #status = False
    except KeyboardInterrupt:
        GPIO.cleanup()
        dhtDevice.exit()
        print("Exiting...")
        exit(1)


if __name__ == '__main__':

    # get the allsky configuration from /etc/raspap
    conf = get_config('settings_RPiHQ.json',
                      'settings_dewheater.json')
    #print(conf)
    main(conf)

