# Thermal

Thermal imager for the Raspberry Pi using the Panasonic Grid-EYE (AMG83xx) sensor on an Adafruit board and the Pimoroni UnicornHD HAT for the display.

The python program reads the 8 by 8 sensor over I2C and displays the image in a combination of three modes:
  colour - image is black and white, or four tone false colour
  interpolated - image is linearly interpolated to 16x16
  relative - image is coloured in the absolute temperature range or in the recently used range with a 10% adjustment pre cycle from the maximum 

The sensor has a maximum speed of 10 frames per second.

Current imaging code is about 9 frames per second on a Pi Zero.
