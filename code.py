import time
import busio
import digitalio
from digitalio import DigitalInOut, Direction, Pull
import board
import neopixel
import adafruit_rfm69
from adafruit_ms8607 import MS8607
import traceback

# I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Neopixel
led_neo = neopixel.NeoPixel(board.NEOPIXEL, 1)
led_neo.brightness = 0.02

# Pressure, Humidity, Temp
weath_sens = MS8607(i2c)

# RFM69
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.D5)
reset = digitalio.DigitalInOut(board.D6)
rfm69 = adafruit_rfm69.RFM69(spi, cs, reset, 915.0, high_power=True, )



prev_packet = None
# Optionally set an encryption key (16 byte AES key). MUST match both
# on the transmitter and receiver (or be set to None to disable/the default).
#rfm69.encryption_key = b"\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08"


# test that encryption is working
# clean things up into functions
# add acknowledgements: 
# https://learn.adafruit.com/adafruit-rfm69hcw-and-rfm96-rfm95-rfm98-lora-packet-padio-breakouts/advanced-circuitpython-library-rfm9x-rfm69-tweaking-parameters
# https://learn.adafruit.com/adafruit-rfm69hcw-and-rfm96-rfm95-rfm98-lora-packet-padio-breakouts/advanced-circuitpython-rfm69-library-usage


debug_mode = 1
led_neo[0] = (0, 255, 0)

def main():
    while True:
        packet = None
        packet = rfm69.receive()
        # If no packet was received during the timeout then None is returned.
        if packet is None:
            # Packet has not been received
            print("Received nothing! Listening again...")
        else:
            led_neo[0] = (0, 0, 255)
            # raw packet
            print()
            print("Received (raw bytes): {0}".format(packet))

            # processed packet
            packet_text = str(packet, "ascii")
            print("Received (ASCII): {0}".format(packet_text))

            if packet_text == "request_weather\r\n":
                print("Weather request received")

                # do these need to be casted?
                weather_data= ( 
                str(weath_sens.temperature) + "," + 
                str(weath_sens.pressure) + "," + 
                str(weath_sens.relative_humidity)
                )


            
                print(weather_data)
                send_data = bytes(weather_data, "\r\n","utf-8")
                rfm69.send(send_data)
                print("Sent weather data")
                led_neo[0] = (0, 255, 0)
                print("Sent weather data")
                led_neo[0] = (0, 255, 0)


try:  # sometimes the radios get fucky wucky
    print("Running main()")
    print("RSSI: " + str(rfm69.rssi))
    print("Power: " + str(rfm69.tx_power))
    main()
except UnicodeError:    # maybe change to general traceback
    print("Unicode error")
    led_neo[0] = (255, 0, 0)
    #send a message to the server that the request failed has failed
    #main()





# SPDX-FileCopyrightText: 2018 Tony DiCola for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple example to send a message and then wait indefinitely for messages
# to be received.  This uses the default RadioHead compatible GFSK_Rb250_Fd250
# modulation and packet format for the radio.
import board
import busio
import digitalio
import time
import adafruit_rfm69


# Define radio parameters.
RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip, use these if wiring up the breakout according to the guide:
CS = digitalio.DigitalInOut(board.D5)
RESET = digitalio.DigitalInOut(board.D6)
# Or uncomment and instead use these if using a Feather M0 RFM69 board
# and the appropriate CircuitPython build:
# CS = digitalio.DigitalInOut(board.RFM69_CS)
# RESET = digitalio.DigitalInOut(board.RFM69_RST)

# Define the onboard LED
LED = digitalio.DigitalInOut(board.D13)
LED.direction = digitalio.Direction.OUTPUT

# Initialize SPI bus.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialze RFM radio
rfm69 = adafruit_rfm69.RFM69(spi, CS, RESET, RADIO_FREQ_MHZ)

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
yes = 0
while True:
    rfm69.send(bytes("hi mom\r\n", "utf-8"))
    #rfm69.send("Hello world! from feather")
    print("Sent yesnt")
    yes += 1
    print(yes)

   
