from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf
from imagesOled import catOpen, catHappy, catClosed
import time

# Initialize OLED
WIDTH = 128
HEIGHT = 64
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=200000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Clear screen
oled.fill(0)

    

happyCatIMG = framebuf.FrameBuffer(catHappy, 84, 64, framebuf.MONO_HLSB)
closedMouthCatIMG = framebuf.FrameBuffer(catClosed, 64, 64, framebuf.MONO_HLSB)
openMouthCatIMG = framebuf.FrameBuffer(catOpen, 64, 64, framebuf.MONO_HLSB)

"""
def displayText(msg):
    oled.fill(0)
    line = ""
    subMsg = ""
    yCord = 0
    xCord = 0
    for i in range(len(msg)):
        c = msg[i]
        print(subMsg + c + ":")
        if c != " ":
            subMsg += c
            if xCord + len(subMsg) > 16:
                print(f"overflow, {xCord} + {len(subMsg)} = {xCord + len(subMsg)}")
                yCord += 8
                xCord = 0
                line = "" + subMsg
                print("L: " + line)
            if i == len(msg) - 1:
                print(f"last word - {xCord-len(subMsg)}, {yCord}")
                oled.text(subMsg, 8*(xCord), yCord)
                line += subMsg
        else:
            print(f"detected space - {xCord}, {yCord}, {len(subMsg)}")
            oled.text(subMsg, 8*(xCord), yCord)
            line += subMsg + " " 
            xCord += len(subMsg)
            if xCord >= 16:
                print("at end, Line: " + line)
                xCord = 0
                yCord += 8
                line = subMsg + " "
                subMsg = ""
            else:
                print(f"printing space at {xCord}, {yCord}")
                oled.text(" ", 8*(xCord), yCord)
                xCord += 1
                subMsg = ""
               
        print(f"yCord: {yCord}, xCord: {xCord}, subMsg: {len(subMsg)},  I: {i}, Line: {line}")
    oled.show()
    """
    
def displayText(msg):
    oled.fill(0)
    #line = "" # for debugging purpose only - Ignore
    subMsg = ""
    yPos = 0
    xPos = 0
    for i in range(len(msg)):
        c = msg[i] # get current character
        #print(subMsg + c + ":")
        if c != " ": # if the character is not a space
            subMsg += c # add character to current word
            if xPos + len(subMsg) > 16: # if the word is too big to fit on line
                #print(f"overflow, {xPos} + {len(subMsg)} = {xPos + len(subMsg)}")
                yPos += 1 #go to next row
                xPos = 0 # reset x coordinate
                # line = "" + subMsg
                # print("L: " + line)
            if i == len(msg) - 1:
                #print(f"last word - {xPos-len(subMsg)}, {yPos}")
                oled.text(subMsg, 8*xPos, 8*yPos) # put the message at correct coordinate
                # line += subMsg
        else: # current character is a space
            #print(f"detected space - {xPos}, {yPos}, {len(subMsg)}")
            oled.text(subMsg, 8*(xPos), 8*yPos) # put the message at correct coordinate
            # line += subMsg + " "
            xPos += len(subMsg) # shift up x position
            if xPos == 16: # if it is at the end of the row don't print a space
                #print("at end, Line: " + line)
                xPos = 0 # reset xPos
                yPos += 1 # shift down a row
                # line = subMsg + " "
            else: # it is not at end of row so print a space
                #print(f"printing space at {xPos}, {yPos}")
                oled.text(" ", 8*xPos, 8*yPos)
                xPos += 1 # shift up on position
                subMsg = "" # reset word
               
        #print(f"yPos: {yPos}, xPos: {xPos}, subMsg: {len(subMsg)},  I: {i}, Line: {line}")
    oled.show()


oled.fill(0)
oled.blit(happyCatIMG, 0, 0)
oled.show()
time.sleep(1)


while True:
    print("tick")
    
    
    oled.fill(0)
    oled.blit(openMouthCatIMG, 0, 0)
    oled.show()
    time.sleep(.1)
    oled.fill(0)
    oled.blit(closedMouthCatIMG, 0, 0)
    oled.show()
    time.sleep(.1)

