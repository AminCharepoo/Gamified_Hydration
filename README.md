# Gamified Hydration Tracker

An interactive Raspberry Pi Pico-based system that tracks water consumption using a load cell and gamifies hydration through an animated cat companion.

## Overview

This project automatically monitors water intake by weighing your bottle throughout the day. An animated cat on an OLED display reflects your hydration progress, becoming happier as you drink more and thirsty if you fall behind. Personalized daily goals are calculated based on your weight and activity level.

## Features

- **Automatic weight tracking** using HX711 load cell with calibration system
- **Personalized hydration goals** based on body weight and activity level
- **Animated cat companion** with three mood states (Happy, Thirsty open-mouth, Thirsty closed-mouth)
- **Gamified progress system** with milestone checkpoints at 25%, 50%, 75%, and 100%
- **4-hour thirst timer** that resets cat mood if milestones aren't maintained
- **Audio feedback** via buzzer for notifications and milestone celebrations
- **Interactive keypad input** for user data and measurement triggers
- **OLED display** for instructions, progress tracking, and animations

## Hardware Requirements

- Raspberry Pi Pico
- HX711 load cell 
- SSD1306 128x64 OLED display (I2C)
- 4x4 matrix membrane keypad
- Passive buzzer
- Jumper wires and breadboard

## Wiring

| Component | Pico Pin |
|-----------|----------|
| HX711 SCK | GP12 |
| HX711 DT | GP13 |
| OLED SDA | GP0 |
| OLED SCL | GP1 |
| Keypad Rows | GP6, GP7, GP8, GP9 |
| Keypad Cols | GP2, GP3, GP4, GP5 |
| Buzzer | GP17 |

## Software Setup

### Prerequisites
- MicroPython firmware installed on Raspberry Pi Pico
- Thonny IDE or similar MicroPython development environment

### Required Libraries
```python
# Standard MicroPython libraries (pre-installed)
from machine import Pin, I2C, PWM
import time

# External libraries (must be uploaded to Pico)
from hx711_gpio import HX711  # https://github.com/robert-hh/hx711
from ssd1306 import SSD1306_I2C
import framebuf
from imagesOled import catOpen, catClosed, catHappy  # Custom image file
```

## Usage

### Initial Setup

1. **Power on** the system
2. **Press `*`** to start
3. **Calibration** (first time or if needed):
   - Place empty bottle on scale, press `*` to tare
   - Place full bottle on scale
   - Enter bottle weight in oz using keypad, press `*`
4. **Personal info quiz**:
   - Enter your weight in pounds, press `*`
   - Enter activity level (1-5 scale), press `*`
   - System calculates your daily water goal

### Daily Use

1. **Place bottle on scale**, press `*` to measure
2. **Drink water** throughout the day
3. **Remeasure** by placing bottle back and pressing `*`
4. **Watch progress**:
   - Cat becomes happier at 25%, 50%, 75%, 100% milestones
   - Cat becomes thirsty if 4 hours pass without reaching next milestone
   - Buzzer plays sounds for notifications and achievements

## How It Works

### Hydration Calculation
```python
# Daily water goal (oz)
water_oz = weight_lbs * 0.5 * (1 + 0.1 * (activity_level - 1))

# Points calculation
points = (water_consumed / daily_goal) * 100
```

### Milestone System
- Points tracked as percentage of daily goal
- Milestones trigger at 25%, 50%, 75%, 100%
- Cat becomes "Happy" for 4 hours after each milestone
- If 4 hours pass without reaching next milestone, cat becomes "Thirsty"

### Weight Measurement
- HX711 reads load cell with tare offset and scale factor
- 3-sample averaging reduces noise
- Difference from previous measurement = water consumed
- Minimum 5% bottle weight change required to award points

## Configuration

Edit these constants in the code to customize behavior:

```python
# Timing
thirst_timer = 4 * 1000 * 60 * 60  # 4 hours in milliseconds
catDebounce = 10                    # Animation frame rate (ms)
notificationBuffer = 1 * 1000 * 60 * 60    # 1 hour between buzzer alerts

# Thresholds
happyThreshold = 25                 # Percent increase for milestone
```

## Credits

Developed by Amin Charepoo, Paulpavich Sombunsakdikun, Dominic Carr, Lucas Azout

### Resources
- [HX711 MicroPython Library](https://github.com/robert-hh/hx711)
- [SSD1306 OLED Guide](https://www.tomshardware.com/how-to/oled-display-raspberry-pi-pico)
- [Matrix Keypad Tutorial](https://peppe8o.com/use-matrix-keypad-with-raspberry-pi-pico-to-get-user-codes-input/)

---

## Future Improvements

- [ ] Add WiFi connectivity for cloud data logging
- [ ] Implement multiple user profiles
- [ ] Add rechargeable battery for portability
