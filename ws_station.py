import time
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
import adafruit_rfm69
from adafruit_ms8607 import MS8607


# I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Pressure, Humidity, Temp
weath_sens = MS8607(i2c)

# RFM69
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm69 = adafruit_rfm69.RFM69(spi, CS, RESET, 915.0)
prev_packet = None
# Optionally set an encryption key (16 byte AES key). MUST match both
# on the transmitter and receiver (or be set to None to disable/the default).
rfm69.encryption_key = b"\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08"


# maybe add bootleg encryption for fun?
# add acknowledgements: 
# https://learn.adafruit.com/adafruit-rfm69hcw-and-rfm96-rfm95-rfm98-lora-packet-padio-breakouts/advanced-circuitpython-library-rfm9x-rfm69-tweaking-parameters
# https://learn.adafruit.com/adafruit-rfm69hcw-and-rfm96-rfm95-rfm98-lora-packet-padio-breakouts/advanced-circuitpython-rfm69-library-usage



debug_mode = 1


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
        prev_packet = packet # this might need to be this janky due to the if is None thing, idk its not my code
        packet_text = str(prev_packet, "utf-8")
        print(packet_text, 25, 0, 1)
        time.sleep(1) #NOTE can this be shorter?
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


    time.sleep(0.1)
