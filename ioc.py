# Import the basic framework components.
from softioc import softioc, builder
import cothread

#import things required for gpio control

import pigpio
pi1 = pigpio.pi()
IN_PIN = 17
OUT_PIN = 18
# Set the record prefix
builder.SetDeviceName("SISSY2EX:BIOLOGIC:TRIGGER")
builder.SetBlocking(True)


def send_trigger(pin):

    user_gpio = pin
    pulse_len= 100
    pi1.gpio_trigger(OUT_PIN, pulse_len, 1)

# Create some records
in_pin_rb = builder.boolIn('INRB', ZNAM="Off", ONAM="On")
out_pin_rb = builder.boolIn('OUTRB', ZNAM="Off", ONAM="On")
out_pin_sp = builder.boolOut('OUTSP', ZNAM="Off", ONAM="On", on_update=lambda v: pi1.write(OUT_PIN,v))
trigger = builder.Action('SEND', on_update=send_trigger(OUT_PIN))


# Boilerplate get the IOC started
builder.LoadDatabase()
softioc.iocInit()

# Start processes required to be run after iocInit
def update():
    while True:
        in_pin_rb.set(pi1.read(IN_PIN))
        out_pin_rb.set(pi1.read(OUT_PIN))
        cothread.Sleep(1)


cothread.Spawn(update)

# Finally leave the IOC running with an interactive shell.
softioc.interactive_ioc(globals())
