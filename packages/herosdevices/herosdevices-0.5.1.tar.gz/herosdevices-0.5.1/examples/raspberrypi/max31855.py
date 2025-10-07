"""
Example script to extract the temperature from multiple MAX31855 connected to a Raspberry Pi.

Pinout (rpi.gpio naming scheme):
    CLK: 7
    MISO: 5

To support multiple sensors, we connect each with a unique CS pin.
The mapping between CS pin and sensor names is given via the cs_pin_dict.

{
    "sensor_name": CS pin,
    ...
}
"""

from herosdevices.hardware.raspberrypi.max318xx.max31855 import MAX31855

if __name__ == "__main__":
    cs_pin_dict = {"a": 21, "b": 20, "c": 16, "d": 12, "e": 26, "f": 19, "g": 13, "h": 6}
    sensor_bus = MAX31855(cs_pins=cs_pin_dict, miso_pin=5, clk_pin=7)
    print(sensor_bus._observable_data())
