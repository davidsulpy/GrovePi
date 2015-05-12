import time
import math
from threading import Thread, Event
import grovepi
from grove_rgb_lcd import *
from ISStreamer.Streamer import Streamer

streamer = Streamer(bucket_name="GrovePi", 
    #bucket_key="grovepi_20150512", 
    ini_file_location="./isstreamer.ini",
    buffer_size=20)

dht_sensor_port = 7		# Connect the DHt sensor to port 7
sound_sensor = 0        # port A0
light_sensor = 1        # port A1
ult_ranger = 2

def stream_temp(stop_event):
    while (not stop_event.is_set()):
        try:
            # get temp and humidity from DHT sensor
            [ temp,hum ] = grovepi.dht(dht_sensor_port,1)
            if (not math.isnan(temp) and temp != -1):
                temp = temp * 10 / 256.0
                streamer.log("Temperature (C)", temp)
            
            if (not math.isnan(hum) and hum != -1):
                hum = hum * 10 / 256.0
                streamer.log("Humidity (%)", hum)

            setRGB(0,128,64)
            setRGB(0,255,0)
            setText("Temp:" + str(temp) + "C      " + "Humidity :" + str(hum) + "%")
        except (IOError, TypeError):
            print "DHT Error"

    print "dht stream finished"

def stream_sound(stop_event):
    while (not stop_event.is_set()):
        try:
            sound_level = grovepi.analogRead(sound_sensor)
            streamer.log("Sound Level", sound_level)
        except (IOError, TypeError):
            print "Sound Error"
        time.sleep(.5)

    print "sound stream finished"

def stream_distance(stop_event):
    while (not stop_event.is_set()):
        try:
            distance = grovepi.ultrasonicRead(ult_ranger)
            streamer.log("Distance (cm)", distance)
        except (IOError, TypeError):
            print "Range Error"
        time.sleep(.5)

    print "distance stream finished"

def stream_light(stop_event):
    while (not stop_event.is_set()):
        try:
            light_intensity = grovepi.analogRead(light_sensor)
            streamer.log("Light Intensity", light_intensity)
        except (IOError, TypeError):
            print "Light Error"
        time.sleep(.5)

    print "light stream finished"


if __name__ == "__main__":
    stop_event = Event()
    t_temp = Thread(target=stream_temp, kwargs={"stop_event": stop_event})
    t_temp.daemon = False
    t_sound = Thread(target=stream_sound, kwargs={"stop_event": stop_event})
    t_sound.daemon = False
    t_dist = Thread(target=stream_distance, kwargs={"stop_event": stop_event})
    t_dist.daemon = False
    t_light = Thread(target=stream_light, kwargs={"stop_event": stop_event})
    t_light.daemon = False


    t_temp.start()
    t_sound.start()
    t_dist.start()
    t_light.start()

    stop = raw_input("press [ENTER] to end")

    stop_event.set()
    streamer.close()