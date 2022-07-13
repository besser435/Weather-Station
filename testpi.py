


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

# Optionally set an encryption key (16 byte AES key). MUST match both
# on the transmitter and receiver (or be set to None to disable/the default).
rfm69.encryption_key = (
    b"\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08"
)

# Print out some chip state:
print("Temperature: {0}C".format(rfm69.temperature))
print("Frequency: {0}mhz".format(rfm69.frequency_mhz))
print("Bit rate: {0}kbit/s".format(rfm69.bitrate / 1000))
print("Frequency deviation: {0}hz".format(rfm69.frequency_deviation))

# Send a packet.  Note you can only send a packet up to 60 bytes in length.
# This is a limitation of the radio packet size, so if you need to send larger
# amounts of data you will need to break it into smaller send calls.  Each send
# call will wait for the previous one to finish before continuing.


# Wait to receive packets.  Note that this library can't receive data at a fast
# rate, in fact it can only receive and process one 60 byte packet at a time.
# This means you should only use this for low bandwidth scenarios, like sending
# and receiving a single message at a time.
print("Waiting for packets...")
while True:
    get_update = bytes("request_weather\r\n", "utf-8")
    rfm69.send(get_update)
    rfm69.send(bytes("Hi Mom\r\n", "utf-8"))
    print("Sent weather request")


    
    packet = rfm69.receive()
    # Optionally change the receive timeout from its default of 0.5 seconds:
    # packet = rfm69.receive(timeout=5.0)
    # If no packet was received during the timeout then None is returned.
    if packet is None:
        # Packet has not been received
        print("Received nothing! Listening again...")
    else:
        # Received a packet!
        # Print out the raw bytes of the packet:
        print("Received (raw bytes): {0}".format(packet))
        # And decode to ASCII text and print it too.  Note that you always
        # receive raw bytes and need to convert to a text format like ASCII
        # if you intend to do string processing on your data.  Make sure the
        # sending side is sending ASCII data before you try to decode!



        packet_text = str(packet, "ascii")
        print("Received (ASCII): {0}".format(packet_text))

        if packet_text == "hi mom\r\n":
            print("received a certain message")

      