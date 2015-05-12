import time
import decimal
from threading import Thread, Event
import grovepi
from grove_rgb_lcd import *
from ISStreamer.Streamer import Streamer

streamer = Streamer(bucket_name="GrovePi", 
    #bucket_key="grovepi_20150512", 
    ini_file_location="./isstreamer.ini",
    buffer_size=20)

dht_sensor_port = 4		# Connect the DHt sensor to port 7
sound_sensor = 0        # port A0
light_sensor = 1        # port A1
ult_ranger = 2

def stream_temp(stop_event):
    # get temp and humidity from DHT sensor
    lastTemp = 0.1          # initialize a floating point temp variable
    lastHum = 0.1           # initialize a floating Point humidity variable
    tooLow = 62.0           # Lower limit in fahrenheit
    justRight = 68.0        # Perfect Temp in fahrenheit
    tooHigh = 74.0          # Temp Too high


    # Function Definitions
    def CtoF( tempc ):
       "This converts celcius to fahrenheit"
       tempf = round((tempc * 1.8) + 32, 2);
       return tempf;

    def FtoC( tempf ):
       "This converts fahrenheit to celcius"
       tempc = round((tempf - 32) / 1.8, 2)
       return tempc;

    def calcColorAdj(variance):     # Calc the adjustment value of the background color
        "Because there is 6 degrees mapping to 255 values, 42.5 is the factor for 12 degree spread"
        factor = 42.5;
        adj = abs(int(factor * variance));
        if adj > 255:
            adj = 255;
        return adj;

    def calcBG(ftemp):
        "This calculates the color value for the background"
        variance = ftemp - justRight;   # Calculate the variance
        adj = calcColorAdj(variance);   # Scale it to 8 bit int
        bgList = [0,0,0]               # initialize the color array
        if(variance < 0):
            bgR = 0;                    # too cold, no red
            bgB = adj;                  # green and blue slide equally with adj
            bgG = 255 - adj;
            
        elif(variance == 0):             # perfect, all on green
            bgR = 0;
            bgB = 0;
            bgG = 255;
            
        elif(variance > 0):             #too hot - no blue
            bgB = 0;
            bgR = adj;                  # Red and Green slide equally with Adj
            bgG = 255 - adj;
            
        bgList = [bgR,bgG,bgB]          #build list of color values to return
        return bgList;

    while (not stop_event.is_set()):
        try:
            temp = 0.01
            hum = 0.01
            [ temp,hum ] = grovepi.dht(dht_sensor_port,1)       #Get the temperature and Humidity from the DHT sensor
            if (CtoF(temp) != lastTemp) and (hum != lastHum) and not math.isnan(temp) and not math.isnan(hum):
                    #print "lowC : ",FtoC(tooLow),"C\t\t","rightC  : ", FtoC(justRight),"C\t\t","highC : ",FtoC(tooHigh),"C" # comment these three lines
                    #print "lowF : ",tooLow,"F\t\tjustRight : ",justRight,"F\t\ttoHigh : ",tooHigh,"F"                       # if no monitor display
                    #print "tempC : ", temp, "C\t\ttempF : ",CtoF(temp),"F\t\tHumidity =", hum,"%\r\n"
                    
                    lastHum = hum          # save temp & humidity values so that there is no update to the RGB LCD
                    ftemp = CtoF(temp)     # unless the value changes
                    lastTemp = ftemp       # this reduces the flashing of the display
                    # print "ftemp = ",ftemp,"  temp = ",temp   # this was just for test and debug
                    
                    bgList = calcBG(ftemp)           # Calculate background colors
                    
                    t = str(ftemp)   # "stringify" the display values
                    h = str(hum)

                    streamer.log("Temperature (F)", t)
                    streamer.log("Humidity (%)", h)
                    # print "(",bgList[0],",",bgList[1],",",bgList[2],")"   # this was to test and debug color value list
                    setRGB(bgList[0],bgList[1],bgList[2])   # parse our list into the color settings
                    setText("Temp:" + t + "F      " + "Humidity :" + h + "%") # update the RGB LCD display
                    
        except (IOError,TypeError) as e:
            print "Error" + str(e)


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