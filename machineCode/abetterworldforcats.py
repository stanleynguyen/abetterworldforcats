###################################################################
#       program for sutd dispenser
###################################################################
import time

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

import firebase
url = "https://shinglez.firebaseio.com"
token = "LMM5MC2Q6G1wCDrbrOMraGETVPCj6CSKBpUS2RtQ"
firebase = firebase.FirebaseApplication(url,token)
########################## set up for sensors######################
sensors = {"100": 12, "75": 16, "50": 20, "25":  21}
GPIO.setup([sensors['100'], sensors['75'], sensors['50'], sensors['25']], GPIO.IN)
    
########################## set up for motors#######################
motor = 5
GPIO.setup(motor, GPIO.OUT)
pwm = GPIO.PWM(motor, 50)


food_spoilt = firebase.get('/dispensers/sutd/food_spoilt')
########################## meals time #############################
breakfast = "08:00:59"
lunch = "13:00:59"
dinner = "20:00:59"
fill_time = None
old_percent = 101
new_percent = old_percent

while 'True':
    hundred = GPIO.input(sensors['100'])
    seventy5 = GPIO.input(sensors['75'])
    fifty = GPIO.input(sensors['50'])
    twenty5 = GPIO.input(sensors['25'])
    ####################code for updating info to cloud#########################
    if hundred == 1 and seventy5 == 1 and fifty == 1 and twenty5 == 1:
        new_percent = 100
    elif seventy5 == 1 and fifty == 1 and twenty5 == 1:
        new_percent = 75
    elif fifty == 1 and twenty5 == 1:
        new_percent = 50
    elif twenty5 == 1:
        new_percent = 25
    else:
        new_percent = 0
    #update to cloud how much food left
    if new_percent != old_percent:
        if new_percent == 100:
            fill_time = time.time()
            print fill_time
            firebase.put('/', '/dispensers/sutd/last_filled', time.ctime(fill_time))
        firebase.put('/', '/dispensers/sutd/fullness', new_percent)
        old_percent = new_percent
    #update to cloud if the food is spoilt
    if fill_time:
        if time.time()-fill_time >= 172800:
            if food_spoilt == 'False':
                food_spoilt = 'True'
                firebase.put('/', '/dispensers/sutd/spoilt', food_spoilt)
        else:
            if food_spoilt == 'True':
                food_spoilt = 'False'
                firebase.put('/', '/dispensers/sutd/food_spoilt', food_spoilt)
            
    ####################code for controlling the auto-dispensing mechanism#########################
    if breakfast in time.ctime():
        print 'breakfast'
        pwm.start(2.5)
        pwm.ChangeDutyCycle(5)
        time.sleep(1) #how long open lid => amount of food dispensed
        pwm.ChangeDutyCycle(2.5)
        time.sleep(3)
        pwm.stop()
    elif lunch in time.ctime():
        pwm.start(2.5)
        pwm.ChangeDutyCycle(5)
        time.sleep(1) #how long open lid => amount of food dispensed
        pwm.ChangeDutyCycle(2.5)
        time.sleep(3)
        pwm.stop()
    elif dinner in time.ctime():
        pwm.start(2.5)
        pwm.ChangeDutyCycle(5)
        time.sleep(1) #how long open lid => amount of food dispensed
        pwm.ChangeDutyCycle(2.5)
        time.sleep(3)
        pwm.stop()
