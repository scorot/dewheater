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
import string


class DewHeater(object):
    """
    """
    def __init__(self, dewheater_conf_file):
        self.allsky_conf_file = None
        self.dewheater_conf_file = dewheater_conf_file
        self.config = {}
        self.heater_status = False
        self.verbose_log = False


    def get_config(self, verbose=1):
        """Read allsky json config file to get the location
        and also read the dew heater json config file.

        Returns a dictionnary with all the configuration
        parameters.
        """

        dewheater_conf_file = os.path.basename(self.dewheater_conf_file)
        if os.path.exists("/home/pi/allsky/dewheater/" + dewheater_conf_file):
            if verbose:
                print("Read {}".format("/home/pi/allsky/dewheater/" + dewheater_conf_file))
            with open("/home/pi/allsky/dewheater/" + dewheater_conf_file, 'r') as fc:
                 j = json.load(fc)
            self.dewheater_conf_file = "/home/pi/allsky/dewheater/" + dewheater_conf_file
        else:
            raise IOError(" ".join(("dewheater config file not found. You must copy",
                          "settings_dewheater.json.repo to settings_dewheater.json",
                          "and change the settings according to your setup.")))

        allsky_conf_file = j.get("allsky_config_file")
        
        if os.path.exists("/home/pi/allsky/dewheater/" + allsky_conf_file):
            if verbose:
                print("Read {}".format("/home/pi/allsky/dewheater/" + allsky_conf_file))
            with open("/home/pi/allsky/dewheater/" + allsky_conf_file, 'r') as fc:
                j.update(json.load(fc))
            self.allsky_conf_file = "/home/pi/allsky/dewheater/" + allsky_conf_file
        elif os.path.exists("/home/pi/allsky/config/" + allsky_conf_file):
            if verbose:
                print("Read {}".format("/home/pi/allsky/config/" + allsky_conf_file))
            with open("/home/pi/allsky/config/" + allsky_conf_file, 'r') as fc:
                j.update(json.load(fc))
            self.allsky_conf_file = "/home/pi/allsky/config/" + allsky_conf_file
        else:
            raise IOError(f"allsky config {allsky_conf_file} file not found. Check your {dewheater_conf_file} file.")

        if verbose:
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
        if verbose:
            print("loop sleep time is {}s".format(j.get("loop_sleep_time")))
        if j.get("verbose_log") == 1:
            self.verbose_log = True
        self.config = j


    def dew_point(self, temp, rh):
        """Compute dew point temperature from temperature
        and relative humidity percentage.
        """
        b = 18.678
        c = 257.14
        gamma = log(rh/100.) + ( b * temp / (c + temp))
        temp_dp = (c * gamma) / (b - gamma) 

        return temp_dp


    def get_owm_ext_data(self):
        """Get outdoor temperature en relative humidity from
        OpemWeaterhMap.
        """    
        api_key = self.config.get('owm_api_key')
        lat = self.config.get('latitude')
        longi = self.config.get('longitude')

        owm = pyowm.OWM(api_key)
        mgr = owm.weather_manager()
        obs = mgr.weather_at_coords(lat, longi)
        temp = obs.weather.temperature('celsius').get('temp')
        humidity = obs.weather.humidity

        return temp, humidity


    def set_heater_on(self):
        """Activate the heater relay.
        """
        pin = self.config.get('relay_board_pin')
        status = self.heater_status

        if status == False:
            GPIO.output(pin, True)
            #now = datetime.now()
            #current_time = now.strftime("%d/%m/%Y-%H:%M:%S")
            print("Turn on heater")
            self.heater_status = True
        else:
            #print("Heater allready on. Keep it on")
            self.heater_status = status


    def set_heater_off(self):
        """De-activate the heater relay.
        """
        pin = self.config.get('relay_board_pin')
        status = self.heater_status

        if status == True:
            GPIO.output(pin, False)
            #now = datetime.now()
            #current_time = now.strftime("%d/%m/%Y-%H:%M:%S")
            print("Turn off heater")
            self.heater_status = False
        else:
            #print("Heater allready off. Keep it off")
            self.heater_status = status

    def get_board_from_pin(self):
        """Translate pin number given as interget in the
        json file into a adafruit board class object.
        """

        pin = self.config.get("dht22_board_pin")
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

    def wait_or_conf_mod(self):
        """sleep for an given delay in seconds or 
        tdetect changes in the configuration file.
        """

        fileName = self.dewheater_conf_file
        originalTime = os.path.getmtime(fileName)

        timeout = self.config.get("loop_sleep_time")
        if self.verbose_log:
            print('Sleep for {} seconds...'.format(timeout))
        while(timeout > 0.):
            if(os.path.getmtime(fileName) > originalTime):
                # Reread the configuration file
                if self.verbose_log:
                    print('Configuration file has changed. Reread configuration file.')
                self.get_config(verbose=False)
                #print(self.config) 
                break
                #originalTime = os.path.getmtime(fileName)
            timeout = timeout - 5.0 
            time.sleep(5.0)

    def summary(self, data_line):
        """Write the data_line in a file
        """
        with open('/home/pi/allsky/dewheater/summary.txt', 'w') as f:
            f.write(data_line)

    def main(self):

        #datalogger = os.path.join('/var', 'log', datalogger)
        #datalogger = '/var/log/dewheater_data.log'
        datalogger = '/home/pi/allsky/tmp/dewheater_data.log'
        logging.basicConfig(filename=datalogger,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.INFO)

        relaypin = self.config.get("relay_board_pin")
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        #GPIO.setmode(GPIO.BOARD)
        GPIO.setup(relaypin, GPIO.OUT)

        dht22_board_pin = self.get_board_from_pin()
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

        status = True
        try: 
            while True:
                try:
                    # Print the values to the serial port
                    temp_in = dhtDevice.temperature
                    humidity_in = dhtDevice.humidity
                    dewpoint_in = self.dew_point(temp_in, humidity_in)

                    temp_ext, humidity_ext = self.get_owm_ext_data()
                    dewpoint_ext = self.dew_point(temp_ext, humidity_ext)

                    tdiff = self.config.get("dew_temp_correction")
                    if temp_in < dewpoint_ext + tdiff:
                        if self.verbose_log:
                            print("Internal temperature = {} < {:1.2f} + {} ".format(
                                                                     temp_in,
                                                                     dewpoint_ext,
                                                                     tdiff))
                        self.set_heater_on()

                    if temp_in > dewpoint_ext + tdiff + 0.5:
                        if self.verbose_log:
                            print("Internal temperature = {} > {:1.2f} + {}".format(
                                                                     temp_in,
                                                                     dewpoint_ext,
                                                                     tdiff+0.5))
                        self.set_heater_off()

                    self.summary('\n'.join(('Internal temp.: {}',
                                            'Int. dew point: {:1.2f}',
                                            'Int. Hr: {}%',
                                            'Ext. temp.: {}',
                                            'Ext. dew point: {:1.2f}',
                                            'Ext Hr: {}%',
                                            'Dewheater: {}')).format(temp_in,
                                                             dewpoint_in,
                                                             humidity_in,
                                                             temp_ext,
                                                             dewpoint_ext,
                                                             humidity_ext,
                                                             self.heater_status))

                    logging.info('{} {:1.2f} {} {} {:1.2f} {} {}'.format(temp_in,
                                                             dewpoint_in,
                                                             humidity_in,
                                                             temp_ext,
                                                             dewpoint_ext,
                                                             humidity_ext,
                                                             self.heater_status))

                except RuntimeError as error:
                    # Errors happen fairly often, DHT's are hard to read, just keep going
                    #print(error.args[0])
                    time.sleep(5.0)
                    continue
                except Exception as error:
                    dhtDevice.exit()
                    GPIO.cleanup()
                    print(f"An error occured with message: {error}.\nExiting...")
                    exit(1)
                    #raise Exception(str(error))

                # reread the config files in case the user changes some setings
                self.wait_or_conf_mod()

        except KeyboardInterrupt:
            GPIO.cleanup()
            dhtDevice.exit()
            print("Exiting...")
            exit(1)


if __name__ == '__main__':

    # get the allsky configuration from /etc/raspap
    dh = DewHeater('settings_dewheater.json',
                   )

    dh.get_config(verbose=1)
    dh.main()

