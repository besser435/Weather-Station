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


import time
import datetime
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
import adafruit_ssd1306 # OLED display
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
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)
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
rfm69.encryption_key = b"\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08"

"""while True:
    
    packet = None
    # draw a box to clear the image
    display.fill(0)
    display.text("Weather Station", 35, 0, 1)

    # check for packet rx
    packet = rfm69.receive()
    if packet is None:
        display.show()
        display.text("- Waiting for PKT -", 15, 20, 1)
    else:
        # Display the packet text and rssi
        display.fill(0)
        prev_packet = packet
        packet_text = str(prev_packet, "utf-8")
        display.text("RX: ", 0, 0, 1)
        display.text(packet_text, 25, 0, 1)
        time.sleep(1)

    if not btnA.value:
        # Send Button A
        display.fill(0)
        button_a_data = bytes("request_weather\r\n","utf-8")
        rfm69.send(button_a_data)
        display.text("Requested update", 25, 15, 1)


    display.show()
    time.sleep(0.1)
    break#
"""




# options
FILE_NAME = "weather_db.csv" 
file_location = "/home/pi/Desktop/" 
zip_code = "85050"
use_zip = 0
city_name = "phoenix"
weather_api_key = "1392d31baeec1ab9f5d2bd99d5ec04aa"

# storage
last_update = None


while True:
    display.fill(0)
    display.text("Next update in...", 25, 15, 1)

    # log the data every 20 minutes (Only does it onc per hour rn)
    if datetime.datetime.now().minute == 20:
        display.fill(0)
        get_update = bytes("request_weather\r\n","utf-8")
        rfm69.send(get_update)
        display.text("Requested update", 25, 15, 1)
        print("Requested update")
        time.sleep(0.05) #needed? longer? shorter?


    # manually refresh the data
    if not btnA.value:
        display.fill(0)
        button_a_data = bytes("request_weather\r\n","utf-8")
        rfm69.send(button_a_data)
        display.text("Requested update", 25, 15, 1)


    # fetch the data from the packet
    packet = None
    display.fill(0)

    packet = rfm69.receive()
    if packet is None:
        display.show()
    else:
        display.fill(0)
        prev_packet = packet
        packet_text = str(prev_packet, "utf-8")
        display.text("RX: ", 0, 0, 1)
        display.text(packet_text, 25, 0, 1)
        

        # returned data
        temp = packet_text.split(",")[0]
        pressure = packet_text.split(",")[1]
        humidity = packet_text.split(",")[2]
        time_date = datetime.datetime.now() # the station has no time, so I have to rely on the Pi's time
        last_update = time_date


       


        # log the data to the file
        with open(file_location + FILE_NAME, "a") as f: 
            f.write("temp,pressure,humidity,time_date\n") # ADD: api_temp, api_pressure, api_humidity, api_conditions, api_time
            f.write(str(temp) + "," + str(pressure) + "," + str(humidity) + "," + str(time_date) + "\n")










    # error checking
    if time_date - last_update > datetime.timedelta(hours=1):
        display.text("Error: No data in last hour", 25, 15, 1)
        with open(file_location + FILE_NAME, "a") as f: 
            f.write("Stale data. last update: " + str(last_update) + "current time: " + time_date + "\n")

        print("Error: No data in last hour")
        time.sleep(0.05)

    display.show()
    time.sleep(0.1)
