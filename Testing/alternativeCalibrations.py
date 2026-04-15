# Use this to calibrate with a regular 16oz waterbottle. This way you don't have to know weight of your waterbottle
def calibrateWeightWith16oz():
    print("Warming up...")
    time.sleep(2)

    # Tare
    print("Place nothing on the scale and press the button to tare")
    displayText("Place nothing on the scale and press the button to zero")
    while BTN_PIN.value() == 0:
        continue;
    waitForButtonRelease()
    hx.tare() # ZERO THE SCALE
    print("Tare done, offset: ", hx.OFFSET)
    displayText("Done")

    # Step 2: User provides known weight
    print("Place 16oz waterbottle on scale and press button")
    displayText("Place 16oz waterbottle on scale and press button")
    while BTN_PIN.value() == 0:
        continue
    waitForButtonRelease()
    
    known_weight = 16 # oz
    fullBottleWeight = known_weight
   
    #debug: known: {known_weight}")

    # Step 3: Take raw reading
    print("Reading raw value...")
    time.sleep(1)  # wait a bit for stabilization
    raw_value = hx.read_average()  # tare-corrected raw value
    print(f"Raw value measured: {raw_value}")

    # Step 4: Calculate scale factor
    scale_factor = (raw_value - hx.OFFSET) / known_weight # raw value per unit of weight
    hx.set_scale(scale_factor)
    print(f"Calibration complete. Scale factor: {scale_factor}\n")
    displayText("Calibration done")
   
    return fullBottleWeight