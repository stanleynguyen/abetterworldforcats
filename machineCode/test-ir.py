import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup([12, 16, 20, 21], GPIO.IN)
while True:
        print '12',GPIO.input(12)
        print '16', GPIO.input(16)
        print '20', GPIO.input(20)
        print '21', GPIO.input(21)
        print '------------------'
        time.sleep(1)
