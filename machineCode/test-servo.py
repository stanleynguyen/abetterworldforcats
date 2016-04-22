import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.OUT)
pwm = GPIO.PWM(5, 50)
pwm.start(2.5)

count=0
while count<3:
    print count
    print 'open'
    pwm.ChangeDutyCycle(5)
    time.sleep(1)
    print 'close'
    pwm.ChangeDutyCycle(2.5)
    time.sleep(3)
    count+=1

pwm.stop()
