"""
Things to log:
Temp, pressure, humidity, time, weather data from weather api on Pi, errors


Host Features:
Uploads database to its own github repo
Displays last readings
if no data in an hour, displays an error
button to refresh (not log) new data

Last answer
https://forums.raspberrypi.com/viewtopic.php?t=304628


to do:
Add weather API data
Add error logging for station and server
Clean up csv structure


"""


version = "Weather Station v1.0 (Server)"
print(version)

from colorama import init  
init()
from colorama import Fore, Back, Style
init(autoreset=True)
import time
import datetime
import traceback
from requests import request
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
import adafruit_ssd1306 # OLED display, this library is deprecated. update to displayio
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

# 128x32 OLED Display
reset_pin = DigitalInOut(board.D4)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin) # OLD
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
got_update_this_min = False # so that we don't log data multiple times when it is time to log
current_display_page = 0


with open(file_location + FILE_NAME, "a") as f: 
    f.write("temp,pressure,humidity,transmission_no,time_date\n") # ADD: api_temp, api_pressure, api_humidity, api_conditions, api_time

display.fill(0)
display.text("Starting", 28, 13, 1)
display.show() 

# this stuff is so errors dont happen when there is no data.
# for example when the program first starts
temp = None
pressure = None
humidity = None
trans_no = None


try:
    def display_info(page):
        #get_update(0) #probably best to leave this out here, so we have more control. we dont want to
        # get_update(1), display_info(), get_update(0). that might cause bugs, idk
        dt_time = datetime.datetime.now()
        time_date = dt_time.strftime("%m-%d-%Y, %H:%M:%S") 
        
        if page == 0:
            display.fill(0)
            display.text("Temp, update, time:", 0, 0, 1)
            display.text(str(temp) + "c", 0, 13, 1)
            # the last time data was added to the DB and the current time
            display.text(
            "DBU: " + str(last_update) + 
            " T: " + str(dt_time.strftime("%H")) + ":" + str(dt_time.strftime("%M")), 0, 25, 1
            )
            display.show()

        if page == 1:
            display.fill(0)
            display.text(("%.1f" % float(temp)) + "c    " + "%.1f" % ((float(temp) * 1.8) + 32) + "f", 0, 0, 1) # HOLY FUCK
            display.text("%.1f" % float(pressure) + "mbar", 0, 13, 1)
            display.text("%.1f" % float(humidity) + "%    #: " + str(trans_no), 0, 25, 1)
            display.show() 

        if page == 2:
            display.fill(0)
            display.text("Stored Data", 27, 13, 1)
            display.show()
            time.sleep(2)
            display_info(current_display_page)    
    

    def get_update(store):
        # store is to determine if it will store the data to the DB,
        # or just fetch an update to display numbers and not store it
        global temp, pressure, humidity, time_date, dt_time, trans_no, last_update

        packet = None
        packet = rfm69.receive(keep_listening=True)
        #packet = rfm69.receive(keep_listening=True, timeout=1.0)
        if packet is None:
            print("Received nothing! Listening again...")
            
        else:
            #prev_packet = packet
            # returned data
            packet_text = str(packet, "ascii")
            #print("Received (formatted): " + packet_text)
            temp = packet_text.split(",")[0]
            pressure = packet_text.split(",")[1]
            humidity = packet_text.split(",")[2]
            trans_no = packet_text.split(",")[3]
            dt_time = datetime.datetime.now()
            time_date = dt_time.strftime("%m-%d-%Y, %H:%M:%S") 
            print("Temp: " + temp)
            print("Pressure: " + pressure)
            print("Humidity: " + humidity)
            print("Time: " + str(time_date))
            print("Transmission #: " + trans_no)
            print()

            if store == 1:
                print(Fore.GREEN + "Storing data to DB...")
                # log the data to the file
                with open(file_location + FILE_NAME, "a") as f: 
                    f.write(str(temp) + "," + str(pressure) + "," + str(humidity)
                    + "," + str(trans_no) + "," + str(time_date) + "\n")

                last_update = str(dt_time.strftime("%H")) + ":" + str(dt_time.strftime("%M"))
                display_info(2)
                #display.fill(0)
                #display.text("Got update", 0, 0, 1)
                #display.show()
                #time.sleep(1)

            else:
                print(Fore.RED + "Not storing data to DB")
    get_update(0)
    display_info(0)

    def main():
        get_update(1)
        global current_display_page, got_update_this_min
        while True:
            get_update(0)
            display_info(current_display_page)
            if datetime.datetime.now().minute % 10 == 0 and got_update_this_min == False:
                #if True: # for testing
                print("Auto refresh")
                get_update(1)
                display_info(0)
                time.sleep(1)
                got_update_this_min = True  # prevents multiple updates per minute, only want one
                print(Fore.YELLOW + str("got_update_this_min time condition " + str(got_update_this_min)))

            if datetime.datetime.now().minute % 10 != 0:    # reset the var so its ready for next time
                got_update_this_min = False
                
            if not btnA.value: 
                current_display_page = 0
                get_update(0) 
                display_info(0)
                
            if not btnB.value:
                current_display_page = 1
                get_update(0) 
                display_info(1)

            if not btnC.value:
                get_update(1)     
    main()


except Exception:
    # sometimes the radio receives its own request for some reason. 
    # It will also throw temp and display errors if there is no connection to the station
    print(Fore.RED + "f-fucky wucky detected! Getting any telwemitry fwom the station?") # war crime soup
    print(traceback.format_exc())
    display.fill(0)
    display.text("Error, stopping.", 0, 0, 1)
    display.show() 
    