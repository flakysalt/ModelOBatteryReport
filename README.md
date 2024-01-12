# ModelOBatteryReporter

Reports battery status of Model O mouse to the user via Windows Toasts<p>
Built with pyinstaller and has optional support for an Arduino to display battery status

## Usage
Download the latest release and execute the application. The program will run in the background and can be accessed via the Windows tray.

If you have an Arduino, upload the ArduinoBatteryReport.ino to your Arduino and wire it up as shown in the [schematic](https://i0.wp.com/randomnerdtutorials.com/wp-content/uploads/2019/05/oled-display-arduino.png?resize=1024%2C748&quality=100&strip=all&ssl=1)

<img src="https://i0.wp.com/randomnerdtutorials.com/wp-content/uploads/2019/05/oled-display-arduino.png?resize=1024%2C748&quality=100&strip=all&ssl=1" alt="drawing" width="300"/>


## Known Issues
 - Toasts do not show when an application is running in fullscreen cause windows...

## Disclaimer 
Use this at your own risk. I will not take any responsibility if it breaks your mouse.
