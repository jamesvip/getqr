import os
import sys
import random,time
import subprocess

def push_file(file_dir,folder):
    for file in os.listdir(file_dir):
        file_path = os.path.join(file_dir, file)
        if os.path.splitext(file_path)[1] == '.jpg':
            print file
            returnCode1 = subprocess.call('/Users/James/Documents/android/platform-tools/adb push '+file_path+' /sdcard/DCIM/Camera/'+folder+'/'+file, shell=True)
            #print(returnCode1)
            returnCode2 = subprocess.call('/Users/James/Documents/android/platform-tools/adb shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file:///sdcard/DCIM/Camera/'+folder+'/'+file, shell=True)
            #print(returnCode2)
            if returnCode1 == 0 and returnCode2 == 0:
                os.remove(file_path)
print sys.argv[1]
print sys.argv[2]

returnCode = subprocess.call('/Users/James/Documents/android/platform-tools/adb disconnect', shell=True)
time.sleep(1)
returnCode = subprocess.call('/Users/James/Documents/android/platform-tools/adb tcpip 5555', shell=True)
time.sleep(1)
returnCode = subprocess.call('/Users/James/Documents/android/platform-tools/adb connect '+sys.argv[1], shell=True)
print returnCode
time.sleep(1)
if returnCode == 0:
    time.sleep(1)
    returnCode = push_file(sys.argv[2],sys.argv[3])
    time.sleep(1)
returnCode = subprocess.call('/Users/James/Documents/android/platform-tools/adb disconnect', shell=True)
print returnCode