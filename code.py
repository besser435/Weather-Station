from random import randint
import time
import busio
import digitalio
from digitalio import DigitalInOut, Direction, Pull
import board
import neopixel
import adafruit_rfm69
from adafruit_ms8607 import MS8607


version = "Weather Station v1.0 (Station)"
print(version)

# I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Neopixel
led_neo = neopixel.NeoPixel(board.NEOPIXEL, 1)
led_neo.brightness = 0.04

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
# https://learn.adafruit.com/adafruit-rfm69hcw-and-rfm96-rfm95-rfm98-lora-packet-padio-breakouts/advanced-circuitpython-library-rfm9x-rfm69-tweaking-parameters
# https://learn.adafruit.com/adafruit-rfm69hcw-and-rfm96-rfm95-rfm98-lora-packet-padio-breakouts/advanced-circuitpython-rfm69-library-usage


def main():
    cycle = 0
    while True:
        led_neo[0] = (0, 0, 255)

        weather_data= ( 
        str(weath_sens.temperature) + "," + 
        str(weath_sens.pressure) + "," + 
        str(weath_sens.relative_humidity) + "," + 
        str(cycle)
        )

        send_data = bytes(weather_data, "\r\n","utf-8")
        rfm69.send(send_data)
        print(weather_data)
        print("Sent weather data")
        led_neo[0] = (0, 0, 0)
        cycle += 1
        time.sleep(1)

print("Running main()")
print("RSSI: " + str(rfm69.rssi))
print("Power: " + str(rfm69.tx_power))
main()
