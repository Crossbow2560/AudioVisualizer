#include <FastLED.h>

#define NUM_BARS 5
#define LEDS_PER_BAR 5
#define NUM_LEDS (NUM_BARS * LEDS_PER_BAR)
#define LED_PIN 6
#define FADE_SPEED 10

CRGB leds[NUM_LEDS];
float brightnessLevels[NUM_LEDS] = {0};
float targetLevels[NUM_BARS] = {0};

float phases[NUM_BARS] = {0, 1, 2, 3, 4};
float speeds[NUM_BARS] = {0.031, 0.027, 0.037, 0.042, 0.033};

// New: Maximum height for each bar, randomized
int maxHeights[NUM_BARS] = {5, 5, 5, 5, 5};
unsigned long lastMaxHeightUpdate = 0;
const unsigned long maxHeightUpdateInterval = 900; // ms

void setup() {
  FastLED.addLeds<WS2812, LED_PIN, GRB>(leds, NUM_LEDS);
  FastLED.clear();
  FastLED.show();
  randomSeed(analogRead(0));
}

void loop() {
  // Randomize the max height for each bar every so often
  if (millis() - lastMaxHeightUpdate > maxHeightUpdateInterval) {
    lastMaxHeightUpdate = millis();
    for (int i = 0; i < NUM_BARS; i++) {
      maxHeights[i] = random(2, LEDS_PER_BAR + 1); // Between 2 and 5 inclusive
    }
  }

  // --- Generate smooth fake audio bar levels, scaled to each bar's max height ---
  for (int i = 0; i < NUM_BARS; i++) {
    phases[i] += speeds[i];
    if (phases[i] > 6.2831) phases[i] -= 6.2831;
    float base = (sin(phases[i]) + 1.0) * 0.5;
    float noise = random(-10, 11) / 100.0;
    float val = base + noise;
    if (val < 0) val = 0;
    if (val > 1) val = 1;
    float desiredLevel = val * maxHeights[i];
    targetLevels[i] = targetLevels[i] * 0.85 + desiredLevel * 0.15;
  }

  // --- Fading and LED update logic ---
  for (int bar = 0; bar < NUM_BARS; bar++) {
    for (int j = 0; j < LEDS_PER_BAR; j++) {
      int ledIndex = bar * LEDS_PER_BAR + j;
      float ledPos = j + 0.5;
      float levelDiff = targetLevels[bar] - ledPos;
      float targetBrightness = 0;
      if (levelDiff >= 0.5) {
        targetBrightness = 255;
      } else if (levelDiff > -0.5) {
        targetBrightness = (levelDiff + 0.5) * 255.0;
      } else {
        targetBrightness = 0;
      }

      if (brightnessLevels[ledIndex] < targetBrightness) {
        brightnessLevels[ledIndex] += FADE_SPEED;
        if (brightnessLevels[ledIndex] > targetBrightness) brightnessLevels[ledIndex] = targetBrightness;
      } else if (brightnessLevels[ledIndex] > targetBrightness) {
        brightnessLevels[ledIndex] -= FADE_SPEED;
        if (brightnessLevels[ledIndex] < targetBrightness) brightnessLevels[ledIndex] = targetBrightness;
      }

      leds[ledIndex] = CHSV(200 - 10 * bar, 255, (uint8_t)(brightnessLevels[ledIndex] * 60 / 100));
    }
  }

  FastLED.show();
  delay(2);  // ~60 FPS
}
