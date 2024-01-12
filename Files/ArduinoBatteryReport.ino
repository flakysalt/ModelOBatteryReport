/*********
  Rui Santos
  Complete project details at https://randomnerdtutorials.com  
*********/

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

unsigned long previousMillis = 0;        // will store last time the display was updated
const long interval = 900000;            // interval at which to refresh display (5 minutes = 300000ms)
int lastDisplayedNumber = -1;            // store last number displayed


// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

void setup() {
  Serial.begin(9600);

  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3D for 128x64
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);
  }
  delay(2000);

  display.clearDisplay();
  writeHeader();
  // Display static text
  display.setCursor(23,32);
  //display.println("---");
  display.display(); 

}

void loop() {
  unsigned long currentMillis = millis();

  if (Serial.available() > 0) {
    display.clearDisplay();
    writeHeader();
    display.setTextSize(3);
    int incomingNumber = Serial.parseInt();
    display.setCursor(40,32);
    display.println(incomingNumber);
    display.display(); 

  }
  else if (currentMillis - previousMillis >= interval) {
    display.clearDisplay();
    writeHeader();
    // If no new data has been received in the last 5 minutes, refresh the display
    display.setTextSize(1);
    display.setCursor(23,32);
    display.println("No mouse found");
    // Reset the timer
    previousMillis = currentMillis;
    display.display(); 
  }
  delay(500);
}

void writeHeader(){
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(28, 0);
  // Display static text
  display.println("Mouse Battery");
}