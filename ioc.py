# Import the basic framework components.
from cothread.catools import caget, connect, camonitor,caput
from softioc import softioc, builder
import cothread
import numpy as np

import pickle
import json
from os.path import exists


#Read from the save file:
file_path = 'autosave.json'
if exists(file_path):
    with open(file_path) as json_file:
        autosave = json.load(json_file)

# Or make a new one if we don't have any
else:
    autosave = {}


# Set the record prefix
PREFIX = "SISSY2EX:SDD00:mca1"
builder.SetDeviceName(PREFIX)
builder.SetBlocking(True)

#Waveform PV for plotting
energy_waveform = builder.Waveform("ENERGYAXIS",np.linspace(0,1024,1024))

roi_high_pvs =[]
roi_low_pvs =[]

for i in range(32):
    roi_high_pvs.append(builder.aOut("R"+str(i)+"HIENERGY",EGU= "eV",DRVL=-237, DRVH=9918,initial_value= 0, on_update_name=lambda v,name: update_roi(v,name)))
    roi_low_pvs.append(builder.aOut("R"+str(i)+"LOENERGY",EGU="eV",DRVL=-237, DRVH=9918,initial_value= 0, on_update_name=lambda v,name: update_roi(v,name)))
    
values = [0,0,0,"",0]

def update_autosave(pv_name, value):

    autosave[pv_name] = value
    with open(file_path, 'w') as fp:
        json.dump( autosave,fp)

def update_roi(energy,py_pv_name):

    #Determine the PV name we need to write to
    pv_name = py_pv_name.split(PREFIX+":")[1]
    pv_name = pv_name[:-6]
    pv_name = PREFIX + "." + pv_name
    
    #Now determine the appropriate offset 
    offset = values[0]
    slope = values[1]
    quadratic = values[2]

    #ax2 + bx + c = 0 
    a=quadratic
    b=slope
    c=offset-energy

    channel_p = (-b + np.sqrt(b*b - 4*a*c))/ (2*a)
    channel_n = (-b - np.sqrt(b*b - 4*a*c))/ (2*a)

    if channel_p > 0 :
        channel = channel_p
    else:
        channel = channel_n
    
    
    channel = int(np.floor(channel))
    if channel <0:
        channel = 0
    
    caput(pv_name, channel)

    ## Save to file
    update_autosave(py_pv_name,energy)
    

#set up the camonitors
"""
    offset = Cpt(EpicsSignalRO, '.CALO',kind='config')
    slope = Cpt(EpicsSignalRO, '.CALS',kind='config')
    quadratic = Cpt(EpicsSignalRO, '.CALQ',kind='config')
    egu = Cpt(EpicsSignalRO, '.EGU',kind='config')
    two_theta = Cpt(EpicsSignalRO, '.TTH',kind='config')
"""
monitor_pvs = [PREFIX + ".CALO",PREFIX + ".CALS",PREFIX + ".CALQ",PREFIX + ".EGU",PREFIX + ".TTH"]


def calc_waveform(value, index):

    values[index] = value
    offset = values[0]
    slope = values[1]
    quadratic = values[2]
    egu = values[3]
    two_theta = values[4]

    channels = np.linspace(0,1024,1024)
    energy = quadratic*channels**2 + slope*channels+offset
    energy_waveform.set(energy)


camonitor(monitor_pvs,calc_waveform)

# Boilerplate get the IOC started
builder.LoadDatabase()
softioc.iocInit()

# Start processes required to be run after iocInit

# Restore autosave positions
for pv_name in autosave:

    caput(pv_name, autosave[pv_name])


# Finally leave the IOC running with an interactive shell.
softioc.interactive_ioc(globals())
