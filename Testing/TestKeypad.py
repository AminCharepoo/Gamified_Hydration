from machine import Pin
import utime

col_list = [2, 3, 4, 5]
row_list = [6, 7, 8, 9]

for x in range(4):
    row_list[x] = Pin(row_list[x], Pin.OUT)
    row_list[x].value(1)

for x in range(4):
    col_list[x] = Pin(col_list[x], Pin.IN, Pin.PULL_UP)

key_map = [
    ["D", "#", "0", "*"],
    ["C", "9", "8", "7"],
    ["B", "6", "5", "4"],
    ["A", "3", "2", "1"],
]

def Keypad4x4Read(cols, rows):
    for r_idx, r in enumerate(rows):   # pull ONE row low at a time
        r.value(0)
        utime.sleep_us(10)             # let signal settle
        for c_idx, c in enumerate(cols):
            if c.value() == 0:         # key pressed in this row
                r.value(1)
                return key_map[r_idx][c_idx]
        r.value(1)                     # restore before next row
    return None

print("--- Ready to get user inputs ---")
while True:
    key = Keypad4x4Read(col_list, row_list)
    if key is not None:
        print("You pressed: " + key)
        utime.sleep(0.3)