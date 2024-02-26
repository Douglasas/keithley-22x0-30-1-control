#!/usr/bin/env python

import usbtmc
import argparse
import time
from time import sleep
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
from matplotlib.widgets import Button

parser = argparse.ArgumentParser(description='Program a Keithley 2220-30-1 DC power supply')
parser.add_argument('-u', '--usb', help="USB vendor and product IDs", nargs=2, default=['05e6','2220'], required=False, metavar=("VENDOR_ID", "PRODUCT_ID"))


args = parser.parse_args()

#open connection to device
try:
    inst = usbtmc.Instrument(int(args.usb[0], 16), int(args.usb[1], 16))
except usbtmc.usbtmc.UsbtmcException:
    print("Unable to connect to device.")
    exit()
    

#querty device's identity
print(inst.ask("*IDN?"))

NUM_CHANNELS = int(args.usb[1][2])
print(NUM_CHANNELS, "channels")

#start remote control
inst.write("SYSTEM:REMOTE")   

measureing=False

def getSettings():
    vSetting = []
    cSetting=[]
    
    for i in range(0,NUM_CHANNELS):
        inst.write("INST:SEL CH"+str(i+1))
        vSetting.append(inst.ask("VOLT?"))   #voltage setting
        cSetting.append(inst.ask("CURR?"))   #current setting

    return vSetting, cSetting


def getMeasurements():
    measureing=True
    voltStatus =    inst.ask("MEAS:VOLT:DC? ALL")     #voltage on all channels
    currentStatus = inst.ask("MEAS:CURRENT:DC? ALL")  #current on all channels
    
    v = [float(x) for x in voltStatus.split(",")]
    c = [float(x) for x in currentStatus.split(",")]
    measuring=False
    
    return v,c

def isOutput():
    outputStatus = inst.ask("OUTPUT?") 
    if outputStatus == "1":
        return True
    else:
        return False

#check if a string is a number below 30V (device max voltage)
def checkV(s):
    try:
        float(s)
        if float(s) > 30:
            print("Voltage must be less than 30V")
            return False
        return True
    except ValueError:
        return False  

initialSettings = getSettings()


def updateMeasurements(event=0):
    inst.write("*OPC")
    measurements = getMeasurements()
    V1.set_text(f"{measurements[0][0]:.4f}\n{measurements[1][0]:.4f}")
    V2.set_text(f"{measurements[0][1]:.4f}\n{measurements[1][1]:.4f}")
    V3.set_text(f"{measurements[0][2]:.4f}\n{measurements[1][2]:.4f}")

    plt.draw()


def submitChannelV(text, channel: int):
    if checkV(text):
        # inst.write(f"OUTPut {channel}")
        inst.write(f"INST:NSEL {channel}")
        inst.write(f"VOLT {text}")
        updateMeasurements()

def submitChannelC(text, channel: int):
    if checkV(text):
        # inst.write(f"OUTPut {channel}")
        inst.write(f"INST:NSEL {channel}")
        inst.write(f"CURRENT {text}")
        updateMeasurements()

def enableToggle(event):
    outputOn=isOutput()
    buttonString=""
    if outputOn:
        inst.write("OUTPut 0")
        buttonString="Output disabled"
    else:
        inst.write("OUTPut 1")
        buttonString="Output enabled"
    bEnable.label.set_text(buttonString)
    updateMeasurements()



fig = plt.figure(figsize=(5.5,2))
fig.canvas.manager.set_window_title('Keithley 22x0-30-1 Control')
        
axboxCH1V = plt.axes([0.37, 0.23, 0.15, 0.1])
text_boxCH1V = TextBox(axboxCH1V, 'Voltage', initial=initialSettings[0][0])
text_boxCH1V.on_submit(lambda text: submitChannelV(text, 1))

axboxCH2V = plt.axes([0.59, 0.23, 0.15, 0.1])
text_boxCH2V = TextBox(axboxCH2V, '', initial=initialSettings[0][1])
text_boxCH2V.on_submit(lambda text: submitChannelV(text, 2))

axboxCH3V = plt.axes([0.82, 0.23, 0.15, 0.1])
text_boxCH3V = TextBox(axboxCH3V, '', initial=initialSettings[0][2])
text_boxCH3V.on_submit(lambda text: submitChannelV(text, 3))

axboxCH1C = plt.axes([0.37, 0.12, 0.15, 0.1])
text_boxCH1C = TextBox(axboxCH1C, 'Current', initial=initialSettings[1][0])
text_boxCH1C.on_submit(lambda text: submitChannelC(text, 1))

axboxCH2C = plt.axes([0.59, 0.12, 0.15, 0.1])
text_boxCH2C = TextBox(axboxCH2C, '', initial=initialSettings[1][1])
text_boxCH2C.on_submit(lambda text: submitChannelC(text, 2))

axboxCH3C = plt.axes([0.82, 0.12, 0.15, 0.1])
text_boxCH3C = TextBox(axboxCH3C, '', initial=initialSettings[1][2])
text_boxCH3C.on_submit(lambda text: submitChannelC(text, 3))

initialState = isOutput()
initialString = "Output disabled"
if initialState:
    initialString="Output enabled"



axboxEnable = plt.axes([0.4, 0.01, 0.38, 0.1])
bEnable=Button(axboxEnable, initialString)
bEnable.on_clicked(enableToggle)


axboxMeasure = plt.axes([0.4, 0.9, 0.38, 0.1])
bMeasure=Button(axboxMeasure, "Measure")
bMeasure.on_clicked(updateMeasurements)


initialMeasures = getMeasurements()

V1 = plt.text(0.1, -3.5, f"{initialMeasures[0][0]:.4f}\n{initialMeasures[1][0]:.4f}", ha="center", size=12,
              bbox=dict(boxstyle="square",
                   ec=(1., 0.5, 0.5),
                   fc=(1., 0.8, 0.8),
                   ))
V2 = plt.text( 0.7, -3.5, f"{initialMeasures[0][1]:.4f}\n{initialMeasures[1][1]:.4f}", ha="center", size=12,
              bbox=dict(boxstyle="square",
                   ec=(1., 0.5, 0.5),
                   fc=(1., 0.8, 0.8),
                   ))
V3 = plt.text( 1.3, -3.5, f"{initialMeasures[0][2]:.4f}\n{initialMeasures[1][2]:.4f}", ha="center", size=12,
              bbox=dict(boxstyle="square",
                   ec=(1., 0.5, 0.5),
                   fc=(1., 0.8, 0.8),
                   ))
plt.text( -0.55, -3.5, "Voltage\nCurrent", ha="center", size=12)

plt.text(0.1,-1.5, "Channel 1", ha="center", size=12)
plt.text(0.7,-1.5, "Channel 2", ha="center", size=12)
plt.text(1.3,-1.5, "Channel 3", ha="center", size=12)


plt.text(0.1,-5.6, "Channel 1", ha="center", size=12)
plt.text(0.7,-5.6, "Channel 2", ha="center", size=12)
plt.text(1.3,-5.6, "Channel 3", ha="center", size=12)

plt.show()
    
inst.write("SYSTem:LOCal")
inst.close()
    


