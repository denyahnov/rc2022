#!/usr/bin/env python3

from ev3dev2.motor import *
from ev3dev2.sensor import *
from ev3dev2.sensor.lego import *
from ev3dev2.button import Button
from ev3dev2.sound import Sound
from ev3dev2.led import Leds

from math import pi, radians, cos
from traceback import print_exc
from time import sleep

class FilteredSensor:
    def __init__(self):
        self.stored = []
        self.counter = 0
        self.difference = 200
        self.outliers = 15

    def Average(self,values):
        return sum(values) / len(values)

    def GetValue(self,value):
        if self.counter > self.outliers: self.stored = []

        if len(self.stored) == 0: 
            self.stored.append(value)

        old_avg = self.Average(self.stored)

        change = abs(old_avg - value)

        if change >= self.difference:
            self.counter += 1
        else:
            self.stored.append(value)

        return self.Average(self.stored)

class Robot():
    def __init__(self):
        self.a = LargeMotor(OUTPUT_A)
        self.b = LargeMotor(OUTPUT_B)
        self.c = LargeMotor(OUTPUT_C)
        self.d = LargeMotor(OUTPUT_D)

        self.buttons = Button()
        self.sound = Sound()
        self.lights = Leds()

        try:
            self.ultrasonic = UltrasonicSensor(INPUT_4)
            self.ultrasonic_filtered = FilteredSensor()
        except:
            self.ultrasonic = None
            self.ultrasonic_filtered = None

        try:
            self.compass = Sensor(INPUT_3, driver_name = "ht-nxt-compass")
            self.heading = self.compass.value()
        except:
            self.compass = None
            self.heading = None

        try:
            self.fir = Sensor(INPUT_1, driver_name = "ht-nxt-ir-seek-v2")
            self.bir = Sensor(INPUT_2, driver_name = "ht-nxt-ir-seek-v2")

            self.fir.mode = "AC-ALL"
            self.bir.mode = "AC-ALL"
        except:
            self.fir = None
            self.bir = None

        try:
            self.proximity = FilteredSensor()
            self.proximity.difference = 25
        except:
            self.proximity = None

        try:
            self.back_proximity = FilteredSensor()
            self.back_proximity.difference = 15
        except:
            self.back_proximity = None

    def InitVariables(self):
        self.center = self.ultrasonic.distance_centimeters
        self.correction = 15

    def AverageIR(self,values):
        return values[0][0] if values[0][1] >= values[1][1] else values[1][0]

    def AngleToXY(self,angle,speed):
        x = speed * cos(angle)
        y = speed * sin(angle)

        return (x,y)

    def Curve(self,motors,value):
        return [m + value for m in motors]

    def CompassValue(self):
        output = self.compass.value() - self.heading

        if output < 0: output += 360

        return output if output <= 180 else output - 360

    def StartMotors(self,speeds):
        for i in range(len(speeds)): 
            if speeds[i] > 100: speeds[i] = 100
            elif speeds[i] < -100: speeds[i] = -100

        self.a.on(SpeedPercent(speeds[0]))
        self.b.on(SpeedPercent(speeds[1]))
        self.c.on(SpeedPercent(speeds[2]))
        self.d.on(SpeedPercent(speeds[3]))

    def CalcMotors(self,angle,speed):

        fl =  1 * speed * cos(pi / 4 - angle)
        fr = -1 * speed * cos(pi / 4 + angle)
        bl =  1 * speed * cos(pi / 4 + angle)
        br = -1 * speed * cos(pi / 4 - angle)

        return [fr,br,fl,bl]

    def FixSpeeds(self,speeds,maxspeed):
        greatest = max(speeds)

        if greatest > maxspeed: greatest = maxspeed

        fix = maxspeed / greatest

        for i in range(len(speeds)):
            speeds[i] = round(speeds[i] * fix,2)

        return speeds

    def FixAngle(self,ang):
        if ang < 0: ang += 360
        elif ang > 359: ang -= 360

        return ang

    def IRValue(self):
        if self.fir == None or self.bir == None: return [None,None], [None,None]

        fv, bv = self.fir.value(), self.bir.value()

        f = ((fv * 30) - 150) if fv != 0 else None
        b = (bv * 30) if bv != 0 else None

        fs = max([self.fir.value(i) for i in range(1,5)])
        bs = max([self.bir.value(i) for i in range(1,5)])

        if f == None or b == None: return [f,fs], [b,bs]

        return [self.FixAngle(f),fs], [self.FixAngle(b),bs]

    def CalcCompassMotors(self,angle):
        return angle + 4 / -3.5

    def SmoothAngle(self,current,target):
        smoothing = 1.25

        diff = abs(current - target)
        if diff > 270: diff -= 270

        diff /= smoothing

        if current - smoothing / 2 < target: 
            return current + diff
        elif current + smoothing / 2 > target: 
            return current - diff

        return current

    def WallCalc(self,distance):
        if distance > self.center + self.correction:
            return 7
        elif distance < self.center - self.correction:
            return -7
        else:
            return 0

    def Color(self,color):
        self.lights.set_color('LEFT',color)
        self.lights.set_color('RIGHT',color)

    def coast(self):
        self.a.off(brake=False)
        self.b.off(brake=False)
        self.c.off(brake=False)
        self.d.off(brake=False)

    def start(self):
        print("Front",self.fir != None)
        print("Back",self.bir != None)
        print("Compass",self.compass != None)
        print("Ultrasonic",self.ultrasonic != None)
        print("Proximity",self.proximity != None)

        self.InitVariables()

        print("Center",self.center)

        current_angle = 0
        target_angle = 0

        speed = 80

        self.sound.set_volume(20)

        self.sound.play_tone(650,0.3,0,20,self.sound.PLAY_NO_WAIT_FOR_COMPLETE)

        while True:
            self.Color('AMBER')

            while not self.buttons.up:
                if self.buttons.down: return
                sleep(0.1)

            while self.buttons.up:
                if self.buttons.down: return
                sleep(0.1)

            self.Color('GREEN')

            while not self.buttons.up:
                if self.buttons.down: return

                if speed > 80:
                    speed = 80

                f,b = self.IRValue()

                distance = self.ultrasonic_filtered.GetValue(self.ultrasonic.distance_centimeters)
                ball_prox = self.proximity.GetValue(f[1])
                back_prox = self.back_proximity.GetValue(b[1])

                target_angle = self.AverageIR([f,b])

                if target_angle == None:
                    target_angle = 180

                    if speed > 33:
                        speed -= abs(speed - 33) / 2

                    if speed < 33:
                        speed = 33
                else:
                    if speed != 80:
                        speed += abs(80 - speed) / 2

                    avg = max(ball_prox,back_prox)/2

                    scale = 30 * (avg/80)

                    if 15 <= target_angle <= 180:
                        target_angle += scale
                    elif 180 <= target_angle <= 345:
                        target_angle -= scale

                    if 150 <= target_angle <= 180:
                        target_angle += scale * 3
                    elif 180 <= target_angle <= 210:
                        target_angle -= scale * 3

                target_angle -= self.CompassValue()

                angle = self.SmoothAngle(current_angle,target_angle)

                rads = radians(angle)

                motors = self.CalcMotors(rads,speed)

                wall_angle = self.WallCalc(distance)

                if ball_prox > 120 and wall_angle != 0:
                    motors = self.Curve(motors,wall_angle)
                else:
                    #print(self.CompassValue()/2)
                    motors = self.Curve(motors,self.CompassValue()/-2)

                self.StartMotors(self.FixSpeeds(motors,80))

                current_angle = angle
            self.coast()
            self.Color('AMBER')
            self.sound.play_tone(650,0.3,0,20,self.sound.PLAY_NO_WAIT_FOR_COMPLETE)
            sleep(1)
if __name__ == '__main__':
    try:
        robot = Robot()
        robot.start()

        sleep(0.1)
        
        robot.coast()
        robot.Color('GREEN')
    except KeyboardInterrupt:
        robot.coast()
        robot.Color('GREEN')
    except:
        print_exc()