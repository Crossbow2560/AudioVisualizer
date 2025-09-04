import math
import random
import time
from machine import Pin
from neopixel import Neopixel

NUM_BARS = 13
LEDS_PER_BAR = 5
NUM_LEDS = NUM_BARS * LEDS_PER_BAR
DATA_PIN = 28
MACHINE_STATE = 0

led_strip = Neopixel(NUM_LEDS, MACHINE_STATE, DATA_PIN, mode="GRB")
FADE_SPEED = 10

brightness_levels = [0.0 for _ in range(NUM_LEDS)]
target_levels = [0.0 for _ in range(NUM_BARS)]
phases = [i for i in range(NUM_BARS)]
speeds = [random.uniform(0.025, 0.045) for _ in range(NUM_BARS)]
max_heights = [LEDS_PER_BAR for _ in range(NUM_BARS)]
last_max_height_update = time.ticks_ms()
max_height_update_interval = 900

def update_max_heights():
    global max_heights, last_max_height_update
    now = time.ticks_ms()
    if time.ticks_diff(now, last_max_height_update) > max_height_update_interval:
        last_max_height_update = now
        for i in range(NUM_BARS):
            max_heights[i] = random.randint(2, LEDS_PER_BAR)

def bar_to_hue(bar, num_bars):
    return int(43690 + (bar * (54612 - 43690) / (num_bars - 1)))

def main():
    random.seed(int(time.ticks_ms()))
    led_strip.clear()
    led_strip.show()

    while True:
        update_max_heights()

        for i in range(NUM_BARS):
            phases[i] += speeds[i]
            if phases[i] > 2 * math.pi:
                phases[i] -= 2 * math.pi
            base = (math.sin(phases[i]) + 1.0) * 0.5
            noise = random.uniform(-0.10, 0.10)
            val = base + noise
            val = min(max(val, 0), 1)
            desired_level = val * max_heights[i]
            target_levels[i] = target_levels[i] * 0.85 + desired_level * 0.15

        for bar in range(NUM_BARS):
            hue = bar_to_hue(bar, NUM_BARS)
            sat = 255
            for j in range(LEDS_PER_BAR):
                # ROTATE 180 DEGREES
                rotated_bar = NUM_BARS - 1 - bar
                rotated_j = LEDS_PER_BAR - 1 - j
                led_index = rotated_bar * LEDS_PER_BAR + rotated_j

                led_pos = j + 0.5
                level_diff = target_levels[bar] - led_pos
                target_brightness = 0
                if level_diff >= 0.5:
                    target_brightness = 255
                elif level_diff > -0.5:
                    target_brightness = int((level_diff + 0.5) * 255.0)
                else:
                    target_brightness = 0

                if brightness_levels[led_index] < target_brightness:
                    brightness_levels[led_index] += FADE_SPEED
                    if brightness_levels[led_index] > target_brightness:
                        brightness_levels[led_index] = target_brightness
                elif brightness_levels[led_index] > target_brightness:
                    brightness_levels[led_index] -= FADE_SPEED
                    if brightness_levels[led_index] < target_brightness:
                        brightness_levels[led_index] = target_brightness

                val = int(brightness_levels[led_index] * 60 / 100)
                r, g, b = led_strip.colorHSV(hue, sat, val)
                led_strip.set_pixel(led_index, (r, g, b))

        led_strip.show()
        time.sleep(0.02)

if __name__ == "__main__":
    main()
