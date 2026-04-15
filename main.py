"""
Amin Charepoo, Paulpavich Sombunsakdikun, Dominic Carr, Lucas Azout
Professor Jay
Measures the weight of an object using an HX711 and designates points
hx711 repository: https://github.com/robert-hh/hx711
rounding: https://www.w3schools.com/python/ref_func_round.asp
oled display: https://www.tomshardware.com/how-to/oled-display-raspberry-pi-pico
Matrix touchpad: https://peppe8o.com/use-matrix-keypad-with-raspberry-pi-pico-to-get-user-codes-input/
"""

from machine import Pin, I2C, PWM
from hx711_gpio import HX711
import time
from ssd1306 import SSD1306_I2C
import framebuf
from imagesOled import catOpen, catClosed, catHappy

# ----------------HX711 pins ------------------------------------
dt = Pin(13, Pin.IN)
sck = Pin(12, Pin.OUT)
hx = HX711(clock=sck, data=dt)

TARE_OFFSET = -482424.76 
scale_factor = -13203.0520


# --------------USER SETUP -----------------
playerPoints = 0
prevMeasurement = 0

dailyWaterIntake = 110 # average daily water intake in oz
initialWater = 0
totalDrank = 0

# ------- sleep setup --------
sleepTime = 0.01

# -------- DISPLAY SETUP -----------
WIDTH = 128
HEIGHT = 64
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=200000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)
oled.fill(0)

# -------- IMAGES SETUP -----------
happyCatIMG = framebuf.FrameBuffer(catHappy, 84, 64, framebuf.MONO_HLSB)
closedMouthCatIMG = framebuf.FrameBuffer(catClosed, 64, 64, framebuf.MONO_HLSB)
openMouthCatIMG = framebuf.FrameBuffer(catOpen, 64, 64, framebuf.MONO_HLSB)
imgs = [happyCatIMG, openMouthCatIMG, closedMouthCatIMG]

imgState = "Thirsty"    #"Happy", "Thirsty"
catState = "Closed" #"Closed", "Open"

lastDisplayedCat = 0    # ms
catDebounce = 10        # ms
happyThreshold = 25     # percent
lastHappyPercent = 0.0  # percent


# ---- TIMER SETUP ----
thirst_timer = 4 * 1000 * 60 * 60 # ms (14400000ms * 1s/1000ms * 1min/60s * 1hr/60min  = 4hr)
lastMilestone = time.ticks_ms()

# ------- KEYPAD SETUP --------
col_list = [2, 3, 4, 5]
row_list = [6, 7, 8, 9]

for x in range(4): 
    row_list[x] = Pin(row_list[x], Pin.OUT) # setup each row pin as output
    row_list[x].value(1)                    # set each one to high

for x in range(4):
    col_list[x] = Pin(col_list[x], Pin.IN, Pin.PULL_UP) # setup each col pin as input

key_map = [
    ["D", "#", "0", "*"],
    ["C", "9", "8", "7"],
    ["B", "6", "5", "4"],
    ["A", "3", "2", "1"],
]
        
# ------ DISPLAY FUNCTIONS ---------
def displayImg(index, x, y):
    oled.fill(0)
    oled.blit(imgs[index], x, y)
    oled.show()

def displayText(msg):
    oled.fill(0)
    subMsg = ""
    yPos = 0
    xPos = 0
    for i in range(len(msg)):
        c = msg[i]                      # get current character
        if c != " ":                    # if the character is not a space
            subMsg += c                 # add character to current word
            if xPos + len(subMsg) > 16: # if the word is too big to fit on line
                yPos += 1 #go to next row
                xPos = 0 # reset x coordinate
            if i == len(msg) - 1:
                oled.text(subMsg, 8*xPos, 8*yPos) # put the message at correct coordinate
        else: # current character is a space
            oled.text(subMsg, 8*(xPos), 8*yPos) # put the message at correct coordinate
            xPos += len(subMsg)                 # shift up x position
            if xPos == 16:                      # if it is at the end of the row don't print a space
                xPos = 0                        # reset xPos
                yPos += 1                       # shift down a row
                subMsg = ""
            else: # it is not at end of row so print a space
                oled.text(" ", 8*xPos, 8*yPos)
                xPos += 1     # shift up on position
                subMsg = ""   # reset word
    oled.show()

# --- KEYPAD FUNCTIONS ---
def Keypad4x4Read():
    for r_idx, r in enumerate(row_list):   # pull ONE row low at a time
        r.value(0)
        time.sleep_us(10)              # let signal settle
        for c_idx, c in enumerate(col_list):
            if c.value() == 0:         # key pressed in this row
                r.value(1)
                return key_map[r_idx][c_idx]
        r.value(1)                     # restore before next row
    return None

def waitForRelease(): # protects against double pressing
    while Keypad4x4Read() is not None:
        time.sleep_ms(10)
    time.sleep_ms(50)  # extra debounce after release
    
def waitForKey(key = "*"):
    while Keypad4x4Read() != key:
        continue
    waitForRelease()
    
# ---- SCALE FUNCTIONS ----    
# If the offset and scale factor are consistent use this so we don't have to calibrate every time
def setupScale(): 
    hx.OFFSET = TARE_OFFSET
    hx.set_scale(scale_factor)
    return 0

def read_average(times=3, delay=0.05):
    total = 0
    for i in range(times):
        total += hx.get_units()
        time.sleep(delay)
    return total / times
    
# ---- CALIBRATION ----
def calibrateWeight():
    print("Warming up...")
    displayText("Warming up...")

    # Tare
    print("Place nothing on the scale and press * to tare")
    displayText("Place nothing on the scale and press * to zero scale")
    waitForKey("*")
    hx.tare() # ZERO THE SCALE
    print("Tare done, offset: ", hx.OFFSET)

    # User provides known weight
    print("Place your full waterbottle on the scale and press * to measure enter its known weight in oz: ")
    displayText("Place bottle on scale. Enter weight in oz: ")
    user_input = 0
    key = ""
    while key != "*":
        key = Keypad4x4Read()
        if key != None and key != "*":
            print("You pressed: " + key)
            if key.isdigit():
                user_input = user_input * 10 + int(key)
                displayText("Place bottle on scale. Enter weight in oz: " + str(user_input))
                print("Input so far:", user_input)
            else:
                print("Invalid key")
            waitForRelease()
        elif key == "*":
            waitForRelease()
            
    print("user_input:", user_input)
    if user_input == 0:
        known_weight = 17
    else:
        known_weight = user_input
    print("known_weight", known_weight)

    # Take raw reading
    print("Reading raw value...")
    time.sleep(1)  # wait a bit for stabilization
    raw_value = hx.read_average()  # tare-corrected raw value
    print("Raw value measured:", raw_value)

    # Calculate scale factor
    scale_factor = (raw_value - hx.OFFSET) / known_weight # raw value per unit of weight
    hx.set_scale(scale_factor)
    print("Calibration complete. Scale factor:", scale_factor)
    displayText("Complete")
   
    return known_weight



# ---- IMAGE FUNCTIONS ----
def checkImageState():
    global catState, lastDisplayedCat, imgState, lastNotified
    if imgState == "Happy":
        displayImg(0, 22, 0) # img[0] = Happy, x = 32, y = 0
    elif imgState == "Thirsty":
        if (time.ticks_ms() - lastNotified > notificationBuffer):
            playSong(notificationSound)
            lastNotified = time.ticks_ms()
        if (time.ticks_ms() - lastDisplayedCat < catDebounce):
            return
        elif catState == "Closed":
            displayImg(1, 48, 0) # img[1] = Open, x = 0, y = 0
            lastDisplayedCat = time.ticks_ms()
            catState = "Open"
        elif catState == "Open":
            displayImg(2, 48, 0) # img[1] = Closed, x = 0, y = 0
            lastDisplayedCat = time.ticks_ms()
            catState = "Closed"
        else:
            print("INVALID CAT STATE")
            catState = "Closed"
            checkImageState()    
    else:
        print("INVALID STATE")
        imgState = "Happy"
        checkImageState()
        
def checkThirst() :
    global imgState
    if imgState == "Happy":
        elapsed = time.ticks_ms() - lastMilestone
        if elapsed >= thirst_timer:
            imgState = "Thirsty"
            print("Cat is thirsty, did not reach milestone in time")
            
# --- WATER QUIZ ----
def waterQuiz():
    print("How much do you weight in pounds? (press * to submit) ")
    displayText("How much do you weigh in pounds? (press * to submit)")
    key = ""
    weight = 0
    while key != "*":
        key = Keypad4x4Read()
        if key != None and key != "*":
            print("You pressed: " + key)
            if key.isdigit():
                weight = weight * 10 + int(key)
                displayText("How much do you weigh in pounds? (press * to submit): " + str(weight))
            else:
                print("Invalid key")
            waitForRelease()
        elif key == "*":
            waitForRelease()
    if (weight == 0):
        print("Invalid weight, defaulting to 175")
        weight = 175
    print("weight: ", weight)
    
    print("How active are you on a scale from 1-5? ")
    displayText("How active are you on a scale from 1-5? ")
    
    key = ""
    activity = 1
    while key != "*":
        key = Keypad4x4Read()
        if key != None and key != "*":
            print("You pressed: " + key)
            if key.isdigit() and int(key) in range(1, 6):
                activity = int(key)
                displayText("How active are you on a scale from 1-5?: " + str(activity))
            else:
                print("Invalid key")
            waitForRelease()
    waitForRelease()
    print("activity level: ", activity)
    water_oz = weight * 0.5
    water_oz *= (1 + 0.1 * (activity - 1))
    displayText(str(water_oz))
    time.sleep(2)
    return water_oz #this is how much water the person should drink per day

# ---- POINTS AND HYDRATION ----   
def calculatePoints(weight, playerPoints, prevMeasurement, dailyWaterIntake):
    global totalDrank
    if weight > prevMeasurement: # check if weight has increased
        return playerPoints, weight
   
    difference = prevMeasurement - weight
    totalDrank = totalDrank + difference
    print("Diff:", difference)
   
    if initialWater == 0:
        print("Initial water is 0")
        return playerPoints, prevMeasurement
    
    if 100 * difference/initialWater < 5: # check if difference is too small for a point increase
        return playerPoints, prevMeasurement
   
    points = 100 * difference/dailyWaterIntake
   
    hydrationPrint()
   
    return playerPoints + points, weight


def hydrationPrint():
    print("""  / \__
     (    @\___
     /         O
    /   (_____/
     /_____/   U
    """)
    print("Your pet is ", round((totalDrank/dailyWaterIntake)*100, 2), " % hydrated!")


def pointsToImage():
    global lastHappyPercent, lastMilestone

    # current hydration percent
    if(dailyWaterIntake > 0):
        currentPercent = (totalDrank / dailyWaterIntake) * 100
    else:
        currentPercent = 0

    # trigger happy only when you cross the next +15% milestone
    if currentPercent >= lastHappyPercent + happyThreshold:
        lastHappyPercent += happyThreshold
        lastMilestone = time.ticks_ms()
        print("Milestone reached!")
        return "Happy"
    else:
        return None

def check_checkpoints(reached_25, reached_50, reached_75, reached_100):
    percent = playerPoints
    if percent >= 25 and not reached_25:
        reached_25 = True
        print("25% reached!")
        displayImg(0, 22, 0)
        playSong(completedMilestoneSound)
    if percent >= 50 and not reached_50:
        reached_50 = True
        print("50% reached!")
        displayImg(0, 22, 0)
        playSong(completedMilestoneSound)
    if percent >= 75 and not reached_75:
        reached_75 = True
        print("75% reached!")
        displayImg(0, 22, 0)
        playSong(completedMilestoneSound)
    if percent >= 100 and not reached_100:
        reached_100 = True
        print("100% reached!")
        displayImg(0, 22, 0)
        playSong(completedMilestoneSound)
    return reached_25, reached_50, reached_75, reached_100

# ---- BUZZER SETUP ----   

buzzerPin = 17
buzzer = PWM(Pin(buzzerPin))


# frequency for notes 
C5 = 523
E5 = 659
G5 = 784
C6 = 1047

lastNotified = 0 # ms
notificationBuffer = 1*1000*60*60 # 1 hr
playedVictory = False # track if already played completedMilestoneSound 

# sound effects
notificationSound = [
    {"beats": .5, "freq": C5},
    {"beats": .5, "freq": E5},
]

completedMilestoneSound = [
    {"beats": .5, "freq": E5},
    {"beats": .5, "freq": C5},
    {"beats": .5, "freq": E5},
    {"beats": .5, "freq": G5},
    {"beats": .5, "freq": E5},
    {"beats": .5, "freq": G5},
    {"beats": 2, "freq": C6},
]

# buzzer functions
def playtone(frequency):
    buzzer.duty_u16(1000)
    buzzer.freq(frequency)

def bequiet():
    buzzer.duty_u16(0)

def playBeats(note):
    playtone(note["freq"])   
    time.sleep(60/150 * note["beats"])

    bequiet()

def playSong(mySong):
    for note in mySong:
        playBeats(note)
    bequiet()


# ---- STARTUP ----
setupScale()

reached_25 = False
reached_50 = False
reached_75 = False
reached_100 = False

print("PRESS * TO START")
displayText("PRESS * TO START")
waitForKey("*")

print("Place bottle on scale and press * to measure new bottle weight ")
displayText("Place bottle on scale and press *")
waitForKey("*")

prevMeasurement = read_average()
if (prevMeasurement < 0):
    prevMeasurement = 0
initialWater = prevMeasurement
print("Initial water:", initialWater)

"""
prevMeasurement = calibrateWeight()
initialWater = prevMeasurement
"""
dailyWaterIntake = waterQuiz()  # oz
print("Daily water intake: ", dailyWaterIntake, "oz")




# --- MAIN LOOP ----
while True:
    checkThirst()
    checkImageState() # update image on screen
    key = ""
    while key != "*":
        key = Keypad4x4Read()
        checkThirst()
        checkImageState()
        weight = read_average()
        #print("Weight:", weight)
        time.sleep(sleepTime/2)
    waitForRelease()
        
    # measure new water bottle weight
    print("Place bottle on scale and press * to measure new bottle weight ")
    displayText("Place bottle on scale and press *")
    waitForKey("*")
    
    weight = read_average()
    if (weight < 0):
        weight = 0
    
    if prevMeasurement == 0:
        prevMeasurement = weight
        initialWater = prevMeasurement
        print("Initial weight:", initialWater, "oz")
    else:
        print("Previous weight:", prevMeasurement, "oz, Measured Weight:", weight, "oz")
        playerPoints, prevMeasurement = calculatePoints(weight, playerPoints, prevMeasurement, dailyWaterIntake)
        reached_25, reached_50, reached_75, reached_100 = check_checkpoints(reached_25, reached_50, reached_75, reached_100)
        print("Points:", playerPoints)
        displayText("Points: " + str(playerPoints))
        time.sleep(3)
   
   
    newImgState = pointsToImage() # check if milestone got reached
    if newImgState is not None: # only update if milestone is crossed
        imgState = newImgState
    
    time.sleep(sleepTime)
