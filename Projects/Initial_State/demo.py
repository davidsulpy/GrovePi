import time
import grovepi
from grove_rgb_lcd import *
from ISStreamer.Streamer import Streamer

streamer = Streamer(bucket_name="GrovePi", 
    #bucket_key="grovepi_20150512", 
    ini_file_location="./isstreamer.ini")

dht_sensor_port = 7		# Connect the DHt sensor to port 7
sound_sensor = 0        # port A0
light_sensor = 1        # port A1
ult_ranger = 4

def sensor_read():
    while True:
        ## temp/humidity
        try:
            # get temp and humidity from DHT sensor
            [ temp,hum ] = grovepi.dht(dht_sensor_port,1)
            streamer.log("Temperature (C)", temp)
            streamer.log("Humidity (%)", hum)
            t = str(temp)
            h = str(hum)

            setRGB(0,128,64)
            setRGB(0,255,0)
            setText("Temp:" + t + "C      " + "Humidity :" + h + "%")
        except (IOError, TypeError):
            print "DHT Error"

        ##sound
        try:
            sound_level = grovepi.analogRead(sound_sensor)
            streamer.log("Sound Level", sound_level)
        except (IOError, TypeError):
            print "Sound Error"
	   
        ##ult range
        try:
            distance = grovepi.ultrasonicRead(ult_ranger)
            streamer.log("Distance (cm)", distance)
        except (IOError, TypeError):
            print "Range Error"

       ##light
        try:
            light_intensity = grovepi.analogRead(light_sensor)
            streamer.log("Light Intensity", light_intensity)
        except (IOError, TypeError):
            print "Light Error"

	time.sleep(.2)

if __name__ == "__main__":
    try:
        sensor_read()
    except KeyboardInterrupt:
        print "Found Keyboard Interrupt"
        streamer.close()