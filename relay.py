from gpiozero import OutputDevice
from time import sleep

RELAY_PIN = 26
relay = OutputDevice(RELAY_PIN)

relay.on()
sleep(3)
relay.off()
sleep(3)
relay.on()