import time
import math
from grovepi import *
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

def read_temp():
    try:
        # get temp and humidity from DHT sensor
        [ temp,hum ] = dht(dht_sensor_port, 0)
        if (not math.isnan(temp) and temp != -1):
            #temp = temp * 10 / 256.0
            streamer.log("Temperature (C)", temp)
        
        if (not math.isnan(hum) and hum != -1):
            #hum = hum * 10 / 256.0
            streamer.log("Humidity (%)", hum)

        setRGB(0,128,64)
        setText("Temp:" + str(temp) + "C\n" + "Humidity :" + str(hum) + "%")
    except (IOError, TypeError):
        print "DHT Error"

def read_sound():
    try:
        sound_level = analogRead(sound_sensor)
        if (sound_level < 20000 and sound_level > -1):
            streamer.log("Sound Level", sound_level)
    except (IOError, TypeError):
        print "Sound Error"

def read_distance():
    try:
        distance = ultrasonicRead(ult_ranger)
        if (distance < 20000 and distance > -1):
            streamer.log("Distance (cm)", distance)
    except (IOError, TypeError):
        print "Range Error"

def read_light():
    try:
        light_intensity = analogRead(light_sensor)
        if (light_intensity < 20000 and light_intensity > -1):
            streamer.log("Light Intensity", light_intensity)
    except (IOError, TypeError):
        print "Light Error"

def stream_sensors():
    try:
        while True:
            read_light()
            read_distance()
            read_sound()
            read_temp()
            time.sleep(.2)
    except KeyboardInterrupt:
        print "keyboard interrupt detected"

if __name__ == "__main__":
    print "Press Ctl+C to stop"
    stream_sensors()
    streamer.close()