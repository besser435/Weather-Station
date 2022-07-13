import time
import busio
import digitalio
from digitalio import DigitalInOut, Direction, Pull
import board
import adafruit_rfm69
from adafruit_ms8607 import MS8607


# I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Pressure, Humidity, Temp
weath_sens = MS8607(i2c)

# RFM69
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.D5)
reset = digitalio.DigitalInOut(board.D6)
rfm69 = adafruit_rfm69.RFM69(spi, cs, reset, 915.0)


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

while True:
    #packet = None
    packet = rfm69.receive()
    # If no packet was received during the timeout then None is returned.
    if packet is None:
        # Packet has not been received
        print("Received nothing! Listening again...")
    else:
        print()
        # raw packet
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
            print()


# OLD
while True:
    packet = None
    # check for incoming packet
    packet = rfm69.receive()
    if packet is None:
        if debug_mode == 1:
            print("Pressure: %.2f hPa" % weath_sens.pressure)
            print("Temperature: %.2f C" % weath_sens.temperature)
            print("Humidity: %.2f %% rH" % weath_sens.relative_humidity)
        print("Waiting for packet")

    else:
        # Display the packet text and rssi
        print()
        print("Received packet:")



        packet_text = str(packet, "ascii")
        print("Received (ASCII): {0}".format(packet_text))



        prev_packet = packet # this might need to be this janky due to the if is None thing, idk its not my code
        packet_text = str(packet, "ascii")
        #packet_text = str(prev_packet, "utf-8")
        print(packet_text, 25, 0, 1)
        print("Packet rssi:", rfm69.last_rssi)


    if packet_text == "request_weather": #("request_weather\r\n","utf-8")
        print("Weather request received, gathering and transmitting data...")


        print("Pressure: %.2f hPa" % weath_sens.pressure)
        print("Temperature: %.2f C" % weath_sens.temperature)
        print("Humidity: %.2f %% rH" % weath_sens.relative_humidity)


        # do these need to be casted?
        weather_data= ( 
        str("%.2f", weath_sens.temperature) + "," + 
        str("%.2f", weath_sens.pressure) + "," + 
        str("%.2f %%", weath_sens.relative_humidity)
        )
       
       
        send_data = bytes(weather_data, "\r\n","utf-8")
        #send_data = bytes("Button C!\r\n","utf-8")
        rfm69.send(send_data)

        print("Data sent!")






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
    time.sleep(0.1)

   
