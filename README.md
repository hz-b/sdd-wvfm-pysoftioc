## Trigger IOC

This IOC connects to a remote raspberry pi which has been configured to allow remote access to it's GPIO pins. It is intended to send and recieve triggers to a Biologic SP300 Potentiostat, but it could be used for any triggering applications if modified.

This script is to be run on some other machine than the rpi with the pins. It could be run locally on the pi, but developing on a pi is slow!

To pins 17 and 18 a level shifter has been attached which converts the 3.3V from the pi to the 5V expected by the biologic. 

The IOC uses the pigpio library to control the remote pins. Configuration of which IOC to attach to is performed in the start_ioc.sh script. 

| PV |    Description | 
|----------|-------------|
| SISSY2EX:BIOLOGIC:TRIGGER:SEND |  Writing anything to this PV will cause a 100us trigger to be output on pin 18  | 
| SISSY2EX:BIOLOGIC:TRIGGER:DONE |   When we send a trigger this PV goes to 0, it is then put back to 1 when we receive a trigger on pin 17 |  
| SISSY2EX:BIOLOGIC:TRIGGER:INCOUNT | Increments by one every time we recieve a trigger on pin 17. You can monitor this PV to see the time that the trigger is received |  
| SISSY2EX:BIOLOGIC:TRIGGER:OUTCOUNT | Increments by one every time we send a trigger on pin 18 using the $(P):$(R):SEND PV |  

## Intended Use with Biologic

0. Connect the trigger cable from the rPi to the potentiostat DSub9 connector
1. Open the Biologic software of your choice (EC-Lab or EC-Lab express)
2. Connect to the Potentiostat
3. Configure your measurement technique or techniquies
4. Add a trigger in (TI) method at the start of all of your techniques
5. Add a trigger out (TO) method at the end of all your techniques
6. Start your measurement, being sure to select a network drive (like //172.17.9.22/sambashare)
7. Trigger the acquisition using measurement software (Bluesky)
8. The measurement starts and runs
9. The measurement ends and generates a trigger that is registered by this IOC
10. The measurement software (Bluesky) reads the generated file and parses it so it is in the same format as all other data 

## Configuration

Pin 17 -> Input Pin
Pin 18 -> Output Pin (starts at 0)

Output Trigger length = 100us, Trigger is from 0 -> 1 -> 0

## Files

| file |    Description | 
|----------|-------------|
| ioc.py |  python soft IOC which connects to the GPIO pins  | 
| start_ioc.sh |  bash script to set the IP address of the remote rpi |  
| biologic.bob | phoebus .bob display file |  


