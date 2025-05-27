#include <FastLED.h>

#define NUM_LEDS 25  // 5 bars × 5 LEDs each
#define LED_PIN 6    // Adjust this to your setup
#define FADE_SPEED 80  // Controls fade step (higher = faster)

CRGB leds[NUM_LEDS];
int brightnessLevels[NUM_LEDS] = {0};  // Stores LED brightness
int targetLevels[5] = {0, 0, 0, 0, 0};  // Stores target brightness levels

void setup() {
    Serial.begin(115200);
    FastLED.addLeds<WS2812, LED_PIN, GRB>(leds, NUM_LEDS);
    FastLED.clear();
    FastLED.show();
}

void loop() {
    // Read Serial Data
    if (Serial.available()) {
        String data = Serial.readStringUntil('\n');

        if (data.length() == 5) {  // Ensure valid data length
            for (int i = 0; i < 5; i++) {
                targetLevels[i] = constrain(data[i] - '0', 0, 5);
            }
            Serial.println(data);  // Echo back to Python
        }
    }

    // Apply 2-step fading effect
    for (int bar = 0; bar < 5; bar++) {
        for (int j = 0; j < 5; j++) {
            int ledIndex = bar * 5 + j;
            int targetBrightness = (j < targetLevels[bar]) ? 255 : 0;

            // 2-step fade: Jump halfway first, then full brightness
            if (brightnessLevels[ledIndex] < targetBrightness) {
                brightnessLevels[ledIndex] += FADE_SPEED;
                if (brightnessLevels[ledIndex] > targetBrightness) brightnessLevels[ledIndex] = targetBrightness;
            } 
            else if (brightnessLevels[ledIndex] > targetBrightness) {
                brightnessLevels[ledIndex] -= FADE_SPEED;
                if (brightnessLevels[ledIndex] < targetBrightness) brightnessLevels[ledIndex] = targetBrightness;
            }

            // Apply brightness
            //leds[ledIndex] = CHSV(50 * bar, 255, brightnessLevels[ledIndex]); // rainbow type shit
            leds[ledIndex] = CHSV(200-10*bar, 255, brightnessLevels[ledIndex]*(60)/100); // galaxy type shit
        }
    }

    FastLED.show();
    delay(30);  // Controls animation speed
    if(Serial.available() == 0){
      Serial.flush();
    }
}
