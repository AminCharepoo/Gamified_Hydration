from machine import Pin, PWM
from time import sleep

buzzerPin = 17
buzzer = PWM(Pin(buzzerPin))


# frequency for notes 
C5 = 523
E5 = 659
G5 = 784
C6 = 1047

# sound effects
completedObjectiveSound = [
    {"beats": .5, "freq": C5},
    {"beats": .5, "freq": E5},
]

completedGameSound = [
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
    sleep(60/150 * note["beats"])

    bequiet()

def playSong(mySong):
    for note in mySong:
        playBeats(note)
    bequiet()
    
while True:
    playSong(completedObjectiveSound)
    print("Played 1")
    sleep(1)
    playSong(completedGameSound)
    print("Played 1")
    sleep(1)