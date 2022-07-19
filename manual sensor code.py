import busio
from digitalio import DigitalInOut, Direction, Pull
import board
from adafruit_ms8607 import MS8607


# I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Pressure, Humidity, Temp
sensor = MS8607(i2c)

debug_mode = 1

while True:

    # do these need to be casted?
    print("Pressure: %.2f hPa" % sensor.pressure)
    print("Temperature: %.2f C" % sensor.temperature)
    print("Humidity: %.2f %% rH" % sensor.relative_humidity)
    input("Press Enter to continue...")