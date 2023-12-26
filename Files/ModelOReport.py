import time
import requests
import base64
import datetime
import getpass
import pystray
import os
import threading
import hid
import signal
from PIL import Image

from win11toast import toast

batteryReportStage = -1

REPO_OWNER="flakysalt"
REPO_NAME="ModelOLogging"
FILE_PATH="Log.txt"
BRANCH="error_logging"
GITHUB_TOKEN="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"


def find_device():
    # Define the criteria
    vendor_id = 0x258A  # Glorious' vendor id
    product_ids = [0x2011, 0x2022]  # Model O product ids
    interface_number = 2  # Feature report interface

    # Get all connected HID devices
    all_devices = hid.enumerate()

    # Filter devices based on the criteria
    matching_devices = [
        d for d in all_devices
        if d['vendor_id'] == vendor_id and
        d['product_id'] in product_ids and
        d['interface_number'] == interface_number
    ]

    # Sort devices by product_id
    matching_devices.sort(key=lambda d: d['product_id'])

    # Return the first matching device or None if no device is found
    return matching_devices[0] if matching_devices else None

def monitor_battery():
    while True:
        try:
            get_battery_status(False)
        except Exception as e:
            logOnline(e)
        finally:
            time.sleep(600)  # Check every 10 minute

def get_battery_status(forcePushNotification = True):
    device_info = find_device()
    if not device_info:
        toast("Wireless Mouse Battery", "No matching device found!", duration='short')
        return

    device = hid.device()
    device.open_path(device_info['path'])

    # Determine if the mouse is wired based on the product ID
    wired = device_info['product_id'] == 0x2011

    # Prepare and send the feature report
    bfr_w = [0] * 65
    bfr_w[3] = 0x02
    bfr_w[4] = 0x02
    bfr_w[6] = 0x83
    device.send_feature_report(bfr_w)

    # Wait for 50 milliseconds
    time.sleep(0.05)

    # Read the feature report
    bfr_r = device.get_feature_report(0, 65)

    # Process the report
    percentage = max(bfr_r[8], 1)
    status = [0xA1, 0xA4, 0xA2, 0xA0, 0xA3].index(bfr_r[1]) if bfr_r[6] == 0x83 else 2

    currentReportStage =-1
    displaymessage = "Current Battery status:\n{}%".format(percentage)
    # Display the battery status
    if status == 0 and not wired:
        if percentage <= 25:
            currentReportStage = 0
        elif 24 <= percentage <= 15:
            currentReportStage = 1
        elif 14 <= percentage <= 5:
            currentReportStage = 2
        else:
            currentReportStage = 3
    elif status == 0 and wired:
        if percentage <= 25:
            currentReportStage = 0
        elif 24 <= percentage <= 15:
            currentReportStage = 1
        elif 14 <= percentage <= 5:
            currentReportStage = 2
        else:
            currentReportStage = 3
        displaymessage =displaymessage + "(Wired)"
    elif status == 1:
        displaymessage = "Mouse Disconnected/asleep"
    elif status == 3:
        displaymessage = "Mouse waking up..."
    else:
        logOnline(f"unknown status : [1:{bfr_r[1]:02X}, 6:{bfr_r[6]:02X}, 8:{bfr_r[8]:02X}]")

    global batteryReportStage
    if(forcePushNotification or (status == 0  and currentReportStage != batteryReportStage)):
        batteryReportStage = currentReportStage
        toast("Wireless Mouse Battery", displaymessage, duration='short')

    device.close()

def logOnline(message):
    print("logging online now")
    # Step 1: Get the current file content
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}",
                            headers=headers)

    response_json = response.json()
    current_content = base64.b64decode(response_json["content"]).decode("utf-8")
    current_sha = response_json["sha"]

    # Step 2: Append text and encode to base64
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    windows_username = getpass.getuser()  # Retrieve Windows username
    new_message = f"{timestamp} - {windows_username} - {message} \n"
    
    new_content = current_content + new_message
    new_content_base64 = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")

    # Step 3: Update the file content
    data = {
        "message": "Append text to file",
        "content": new_content_base64,
        "branch":BRANCH,
        "sha": current_sha
    }

    response = requests.put(f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}",
                            json=data,
                            headers=headers)

    if response.status_code == 200:
        print("File content updated successfully.")
    else:
        print("Error:", response.status_code)

def exit_program():
    logOnline("Stop Program")
    tray_icon.stop()  # Stop the system tray application
    os.kill(os.getpid(), signal.SIGTERM)  # Terminate the process

def main():
    global tray_icon
    logOnline("Start Program")

    script_directory = os.path.dirname(os.path.abspath(__file__))
    icon_image = Image.open(script_directory + "\\Icon.ico")

    # Define menu items for both left-click and right-click context menus
    menu = (
        pystray.MenuItem("Display Status Now", get_battery_status),
        pystray.MenuItem("Exit", exit_program),
    )

    # Create the tray icon
    tray_icon = pystray.Icon("Mouse Battery Reporter", icon_image, "Mouse Battery Reporter", menu)

    # Start the tray icon in a separate thread
    tray_thread = threading.Thread(target=tray_icon.run)
    tray_thread.start()

    # Start the battery monitoring in the main thread
    monitor_battery()

if __name__ == "__main__":
    main()