from gpiozero import LED, Button
from time import sleep

led = LED(2)
button = Button(3)

for x in range(4):
    button.wait_for_press()
    led.toggle()
    sleep(0.5)