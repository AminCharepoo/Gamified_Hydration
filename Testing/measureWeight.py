"""
Amin Charepoo
Professor Jay
Measures the weight of an object using an HX711 and designates points
hx711 repository: https://github.com/robert-hh/hx711
"""

from machine import Pin
from hx711_gpio import HX711
import time

# HX711 pins
dt = Pin(13, Pin.IN)
sck = Pin(12, Pin.OUT)

hx = HX711(clock=sck, data=dt)

def calibrateWeight():
    print("Warming up...")
    time.sleep(2)

    # Step 1: Tare (zero the scale)
    input("Place nothing on the scale and press Enter to tare")
    hx.tare() # ZERO THE SCALE
    print("Tare done")

    # Step 2: User provides known weight
    known_weight = float(input("Place your full waterbottle on the scale and measure enter its known weight: "))

    # Step 3: Take raw reading
    print("Reading raw value...")
    time.sleep(1)  # wait a bit for stabilization
    raw_value = hx.get_value()  # tare-corrected raw value
    print(f"Raw value measured: {raw_value}")

    # Step 4: Calculate scale factor
    scale_factor = raw_value / known_weight
    hx.set_scale(scale_factor)
    print(f"Calibration complete. Scale factor: {scale_factor}\n")
    
TARE_OFFSET = -482424.76 
scale_factor = -13203.0520
def setupScale(): 
    hx.OFFSET = TARE_OFFSET
    hx.set_scale(scale_factor)
    return 0
    
setupScale()
while True:
    weight = hx.get_units();
    print(f"Weight: {weight}")
    
    time.sleep(0.5)

