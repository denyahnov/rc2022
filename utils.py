#!/usr/bin/env python3

# Check if an Object is Blocking Ultrasonic
def robotNotBlocking(oldDistance, newDistance):
    # Get Distance Change
    distanceChange = abs(oldDistance - newDistance)

    # Check for Rapid Increase in Distance from Wall
    if (distanceChange > 30):
        return False
    else:
        return True

# Get Compass Angle relative to the Goal Angle
def getAngle(angle, centerAngle):
    output = angle - centerAngle

    if output < 0:
        output += 360

    return output

# Check if Robot has Possesion of the Ball
def ballPossesion(centerStrength):
    if 115 < centerStrength < 300:
        return True
    else:
        return False

# 8-Direction Motor Movement
#  1  2  3
#  8  0  4
#  7  6  5
def motorDirection(direction):
    if direction == 0:
        return 0,0,0,0
    elif direction == 1:
        return -1,0,0,1
    elif direction == 2:
        return -1,-1,1,1
    elif direction == 3:
        return 0,-1,1,0
    elif direction == 4:
        return 1,-1,1,-1
    elif direction == 5:
        return 1,0,0,-1
    elif direction == 6:
        return 1,1,-1,-1
    elif direction == 7:
        return 0,1,-1,0
    elif direction == 8:
        return -1,1,-1,1
    elif direction == 9:
        return -0.5,1,-1,0.5
    elif direction == 10:
        return 1,-0.5,0.5,-1
    return 0,0,0,0

# Motor Speed does not go ouotside boundaries
def ms(speed):
    speed=round(speed)
    if speed < -100: return -100
    if speed > 100: return 100
    return speed

# Points towards 'North'
def pointForward(angle,speed):
    left=0 if 358 > angle > 180 else 1
    if 358 > angle > 2:
        if angle > 180:
            angle*=-1
            angle+=360
        percent=round((angle+10)/2)+2
        percent/=-100 if left == 1 else 100
        return speed*percent
    return 0

# Get robot position on field
def getPos(distance,fieldWidth):
    if distance > (fieldWidth+130):
        return 1
    elif distance < (fieldWidth-130):
        return 2
    else:
        return 0

# Convert IR Inputs to a Pos Value and Strength Value
def irToPos(fp,bp,fs,bs):
    if 2 < fp < 8:
        i=(fp)-5
        if i < 0: i+=12
        return i,max(fs)
    elif 2 < bp < 8:
        i=(bp)+1
        if i < 0: i+=12
        return i,max(bs)
    elif fp > 0:
        i=(fp)-5
        if i < 0: i+=12
        return i,max(fs)
    elif bp > 0:
        i=(bp)+1
        if i < 0: i+=12
        return i,max(bs)
    else:
        return -1,-1

# Convert IR position to Motor Direction
def moveBall(pos,strength,dist,fieldWidth,curving,robot_num=1):
    if robot_num == 1:
        if pos == 0: return 2
        if pos == 1: return 3
        if pos == 2: return 5
        if pos == 3: return 6
        if pos == 4: return 6
        if pos == 5: return 6
        if pos == 6:
            if getPos(dist,fieldWidth) == 1:
                return 4
            else:
                return 8
        if pos == 7: return 6
        if pos == 8: return 6
        if pos == 9: return 6
        if pos == 10: return 7
        if pos == 11: return 1
    elif robot_num == 2:
        if pos == 0: return 2
        if pos == 1: return 3
        if pos == 2: return 5
        if pos == 3: return 6
        if pos == 4: return 6
        if pos == 5: return 6
        if pos == 6:
            if getPos(dist,fieldWidth) == 1:
                return 4
            else:
                return 8
        if pos == 7: return 6
        if pos == 8: return 6
        if pos == 9: return 7
        if pos == 10: return 7
        if pos == 11: return 1
    return 0

# Curve towards Goal
def curve(dist,field,speed):
    p=getPos(dist,field)
    if p== 0: return 0
    if p== 1: return round(speed*0.1)
    if p== 2: return round(speed*-0.1)

# Center Robot
def center(dist,field):
    p=getPos(dist,field)
    if p== 0: return 6
    if p== 1: return 4
    if p== 2: return 8
    
# Get Comm State
def commState(state,teammate,server):
    if state == 1 and teammate == 1:
        if server:
            return 1 # Attack
        else:
            return 2 # Defend
    elif state == 2 and teammate == 2:
        if server:
            return 1 # Attack
        else:
            return 2 # Defend
    elif state != 1 and teammate == 1:
        return 2 # Defend
    return state

# Return Ultrasonic Values
def ultrasonicValue(value,values,outliers):
    if len(values) == 0: # List has no values
        values.append(value) # Append Value

    average = sum(values) / len(values)
    change_needed = 200
    change = abs(average - value)

    if outliers > 30: # If Ultrasonic has too many outliers, reset
        values = [value]

    if change < change_needed: # Value is not too great of change
        values.append(value) # Append Value
        outliers = 0
    else:
        outliers += 1 # Add Outlier

    if len(values) > 20: values.pop(0) # List too long

    return values, outliers