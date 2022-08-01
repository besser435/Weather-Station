"""
Architecture:
Pi requests data every 20 minutes of the hour
Station sends data
Pi logs data to .csv file and uploads it to a github repo

Things to log:
Temp, pressure, humidity, time, weather data from weather api on Pi, errors


Host Features:
Uploads database to github repo
Displays last readings
if no data in an hour, displays an error
button to refresh (not log) new data
"""


version = "Weather Station v0.1 (Server)"
print(version)


import time
import datetime

from requests import request
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
import threading
import displayio
#import adafruit_displayio_ssd1306 # NEW LIBRARY
import adafruit_ssd1306 # OLED display, this libary is deprecated. update to displayio


import adafruit_rfm69

# Button A
btnA = DigitalInOut(board.D5)
btnA.direction = Direction.INPUT
btnA.pull = Pull.UP

# Button B
btnB = DigitalInOut(board.D6)
btnB.direction = Direction.INPUT
btnB.pull = Pull.UP

# Button C
btnC = DigitalInOut(board.D12)
btnC.direction = Direction.INPUT
btnC.pull = Pull.UP

# I2C
i2c = busio.I2C(board.SCL, board.SDA)
#i2c = board.I2C() 

# 128x32 OLED Display
reset_pin = DigitalInOut(board.D4)


"""display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
#display_bus = displayio.I2CDisplay(i2c)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)
"""
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin) # OLD


# Clear the display.
display.fill(0)
display.show()
width = display.width
height = display.height

# Configure Packet Radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm69 = adafruit_rfm69.RFM69(spi, CS, RESET, 915.0)
prev_packet = None
# Optionally set an encryption key (16 byte AES key). MUST match both
# on the transmitter and receiver (or be set to None to disable/the default).
#rfm69.encryption_key = b"\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08"





# options
FILE_NAME = "weather_db.csv" 
file_location = "/home/pi/Desktop/" 
zip_code = "85050"
use_zip = 0
city_name = "phoenix"
weather_api_key = "1392d31baeec1ab9f5d2bd99d5ec04aa"

# storage
last_update = None

with open(file_location + FILE_NAME, "a") as f: 
    f.write("temp,pressure,humidity,time_date\n") # ADD: api_temp, api_pressure, api_humidity, api_conditions, api_time

try:
    while True:
        #time.sleep(0.5)
        get_update = bytes("request_weather\r\n", "utf-8")
        
        weekday = str(datetime.datetime.today().weekday())
        current_time = str(datetime.datetime.now().strftime("%I:%M %p"))

        display.fill(0)
        display.text(weekday, 0, 0, 1)
        display.text(current_time, 0, 25, 1)
        display.show()
        
        
        # log the data every 20 minutes (Only does it once per hour rn)
        # fetch an update from every 20 minutes


        #if datetime.datetime.now().minute == 14: # test for exact minute
        #if datetime.datetime.now().minute % 2 == 0:
        if True: # for testing
            display.fill(0)
            rfm69.send(get_update)
            display.text("Requested update", 0, 0, 1)
            display.show()    
            print("Requested update")
            #time.sleep(0.05) #needed? longer? shorter?

        # manually fetch an update
        elif not btnA.value:
            display.fill(0)
            rfm69.send(get_update)
            display.text("Requested update manually", 0, 25, 1)
            display.show()
            print("Requested update manually")


        # the code below should be in a function that the two conditions above call
        # fetch the data from the returned packet
        packet = None
        packet = rfm69.receive(keep_listening=True, timeout=1.0)
        if packet is None:
            print("Received nothing! Listening again...")
            display.fill(0)
            display.text("Received nothing", 0, 0, 1)
            display.show()
        else:
            prev_packet = packet
            packet_text = str(packet, "ascii")
            print("Received (raw bytes): " + str(packet))
            print("Received (formatted): " + packet_text)

            display.fill(0)
            display.text("Got data", 0, 0, 1)
            display.show()
            
            # returned data
            temp = packet_text.split(",")[0]
            pressure = packet_text.split(",")[1]
            humidity = packet_text.split(",")[2]
            time_date = datetime.datetime.now() # the station has no time, so I have to rely on the Pi's time
            last_update = time_date

            print("Temp: " + temp)
            print("Pressure: " + pressure)
            print("Humidity: " + humidity)
            print("Time: " + str(time_date))
            print()
            #time.sleep(1)

        


            # log the data to the file
            with open(file_location + FILE_NAME, "a") as f: 
                f.write(str(temp) + "," + str(pressure) + "," + str(humidity) + "," + str(time_date) + "\n")


        # error checking
        """if time_date - last_update > datetime.timedelta(hours=1):
            display.text("Error: No data in last hour", 25, 15, 1)
            with open(file_location + FILE_NAME, "a") as f: 
                f.write("Stale data. last update: " + str(last_update) + "current time: " + time_date + "\n")

            print("Error: No data in last hour")
            time.sleep(0.05)
        """
        display.show()
        #time.sleep(0.1)
except IndexError:
    # sometimes the radio receives its own request for some reason
    print("F-fucky wucky detected! IndexError bwyte awway out of wange!") # war crime soup


 