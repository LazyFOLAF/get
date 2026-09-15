import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
led=26
GPIO.setup(led, GPIO.OUT)
sun=6
GPIO.setup(sun, GPIO.IN)
while True:
    GPIO.output(led, not GPIO.input(sun))