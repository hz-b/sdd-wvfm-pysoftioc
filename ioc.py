# Import the basic framework components.
from softioc import softioc, builder
import cothread

#import things required for gpio control

import pigpio

pi1 = pigpio.pi()
IN_PIN = 17
OUT_PIN = 18
PULSE_LEN = 100

# Set the record prefix
builder.SetDeviceName("SISSY2EX:BIOLOGIC:TRIGGER")
builder.SetBlocking(True)

trigger_out_counter = builder.longIn('OUTCOUNT', initial_value=0)
trigger_in_counter = builder.longIn('INCOUNT', initial_value=0)
done = builder.boolIn('DONE', initial_value=1, ZNAM="Busy", ONAM="Done")

def cbf(g, L, t):

    """
    A function which will be called when the input pin is triggered
    """
    trigger_in_counter.set(trigger_in_counter.get()+1)
    done.set(1)


def send_trigger(v):

    """
    A function which will be called when the output is triggered
    """

    pi1.gpio_trigger(OUT_PIN, PULSE_LEN, 1)
    trigger_out_counter.set(trigger_out_counter.get()+1) 
    done.set(0)
    
# Create some records
out_pin_rb = builder.boolIn('OUTRB', ZNAM="Off", ONAM="On")
out_pin_sp = builder.boolOut('OUTSP', ZNAM="Off", ONAM="On",initial_value=0,always_update=True, on_update=lambda v: pi1.write(OUT_PIN,v))
trigger = builder.boolOut('SEND', initial_value =0,on_update=lambda v: send_trigger(v),always_update=True)

# Boilerplate get the IOC started
builder.LoadDatabase()
softioc.iocInit()

# Start processes required to be run after iocInit
def update():
    while True:
        out_pin_rb.set(pi1.read(OUT_PIN))
        cothread.Sleep(0.1)


cothread.Spawn(update)

#attach calback to the input pin on the rising edge
cb = pi1.callback(IN_PIN, pigpio.RISING_EDGE, cbf)

# Finally leave the IOC running with an interactive shell.
softioc.interactive_ioc(globals())
