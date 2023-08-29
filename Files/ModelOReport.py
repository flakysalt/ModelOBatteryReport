import time
import subprocess
import requests
import base64
import datetime
import getpass

from win10toast import ToastNotifier

batteryReportStage = 0

REPO_OWNER="flakysalt"
REPO_NAME="ModelOLogging"
FILE_PATH="Log.txt"
GITHUB_TOKEN="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"


def display_notification(percentage):
    logErrorOnline("show low battery toast")
    toaster = ToastNotifier()
    toaster.show_toast("Wireless Mouse Battery", "Low Battery! Please charge soon({}%)".format(percentage), duration=5, icon_path = "Icon.ico")

def display_notification_critical(percentage):
    logErrorOnline("show critical battery toast")
    toaster = ToastNotifier()
    toaster.show_toast("Wireless Mouse Battery", "Very low Battery! Charge ASAP ({}%)".format(percentage), duration=5, icon_path = "Icon.ico")

def monitor_battery():
    while True:
        try:
            battery_report = getBatteryPercentage()

            if(not isErrorMessage(battery_report)):
                battery_percentage = battery_report.replace('%','').rstrip()
                if int(battery_percentage) > 30:
                    batteryReportStage = 0
                elif int(battery_percentage) <= 30 and batteryReportStage != 1:
                    batteryReportStage = 1
                    display_notification(battery_percentage)
                elif int(battery_percentage) <= 10 and batteryReportStage != 2:
                    batteryReportStage = 2
                    display_notification_critical(battery_percentage)
            else:
                logErrorOnline(battery_report)
        except Exception as e:
            logErrorOnline(e)
        
        finally:
            time.sleep(600)  # Check every 10 minute




def monitor_battery_once():
        battery_report = getBatteryPercentage()

        if(not isErrorMessage(battery_report)):
            battery_percentage = battery_report.replace('%','').rstrip()
            print(battery_percentage)
            if int(battery_percentage) > 30:
                display_notification(battery_percentage)
                batteryReportStage = 0
            elif int(battery_percentage) <= 30 and batteryReportStage != 1:
                batteryReportStage = 1
                display_notification(battery_percentage)
            elif int(battery_percentage) <= 10 and batteryReportStage != 2:
                batteryReportStage = 2
                display_notification_critical(battery_percentage)
        else:
            logErrorOnline(battery_report)

def getBatteryPercentage():
    # Define the command and arguments
    command = 'mow.exe'
    arg1 = 'report'
    arg2 = 'battery'

    # Execute the command and capture the output
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    process = subprocess.Popen([command, arg1, arg2], stdout=subprocess.PIPE, stderr=subprocess.PIPE,startupinfo=startupinfo)
    stdout,stderr = process.communicate()

    # Decode the output from bytes to string
    stdout = stdout.decode('utf-8')
    stderr = stderr.decode('utf-8')

    if(stderr):
        logErrorOnline(stderr)

    return stdout

def isErrorMessage(inputString):
    return any(char.isalpha() for char in inputString)

def logErrorOnline(error):
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
    new_message = f"{timestamp} - {windows_username} - {error} \n"
    
    new_content = current_content + new_message
    new_content_base64 = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")

    # Step 3: Update the file content
    data = {
        "message": "Append text to file",
        "content": new_content_base64,
        "sha": current_sha
    }

    response = requests.put(f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}",
                            json=data,
                            headers=headers)

    if response.status_code == 200:
        print("File content updated successfully.")
    else:
        print("Error:", response.status_code)

monitor_battery()
