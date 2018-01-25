# To import the function "envia" from the file "test_NeatoCommands.py"
from test_NeatoCommands import envia
import sys
import serial
import time
from multiprocessing import Process, Queue
import http_viewer
import math
import numpy
import random

x=0
y=0
suma_theta=0


def set(message, timeInMs):
    #print "SET - Message: %s, SleepTimeInMs: %f" %(message, timeInMs);
    ser.write(message+'\r'+'\n');
    time.sleep(abs(timeInMs/1000));
        
def get(message):
    #print "GET - Message: %s" %message;
    ser.write(message+'\r'+'\n');

def get_motors():
	""" Ask to the robot for the current state of the motors. """
	msg = envia(ser, 'GetMotors LeftWheel RightWheel').split('\n')

	# For better understanding see the neato commands PDF.

	L = int(msg[4].split(',')[1])
	R = int(msg[8].split(',')[1])

	return (L, R)

def odometry(L, R):
	global x
	global y
	global suma_theta
	global L_ini, R_ini
	#Implement the pos integration. Assume initial conditions [0,0,0].
	
	#Use global variables, discoment this line
	#global VARIABLES
	new_L, new_R = L - L_ini, R - R_ini

	L_ini = L
	R_ini = R

	delta_d = (new_R+new_L)/2
	delta_th = (new_R-new_L)/24.3
	suma_theta = (suma_theta+delta_th)
	suma_theta = numpy.mod(suma_theta,2*math.pi)
	dx = delta_d*math.cos(suma_theta)
	dy = delta_d*math.sin(suma_theta)
	x = x + dx
	y = y + dy
	return [x,y,suma_theta]

def driveTo(X, Y):
	print('====================')
	L, R = get_motors()
	Odo = odometry(L,R)
	time.sleep(0.1)
	print('inside 1 '+str(Odo[2]))
	DistX = X - Odo[0]
	DistY = Y - Odo[1]
	difAngle = numpy.arctan2(DistY,DistX)
	if Odo[2] - difAngle > 2*math.pi - (Odo[2] - difAngle):
		NewTheta = -(2*math.pi - (Odo[2] - difAngle))
		print('inside 1 '+str(NewTheta))
	else: 
		NewTheta = Odo[2] - difAngle
		print('inside 2 '+str(NewTheta))

	envia(ser, 'SetMotor LWheelDist '+ str(NewTheta*121.5) +' RWheelDist ' + str(-NewTheta*121.5) + ' Speed 120')
	L, R = get_motors()
	PostOdo = odometry(L, R)
	time.sleep(0.1)
	PrevOdo = PostOdo[:]
	PrevOdo[0] = PrevOdo[0] + 1
	while PrevOdo != PostOdo :
		L, R = get_motors()
		PrevOdo = PostOdo[:]
		PostOdo = odometry(L, R)
		time.sleep(0.1)

	Dist = numpy.sqrt(DistX*DistX + DistY*DistY)
	envia(ser, 'SetMotor LWheelDist '+ str(Dist) +' RwheelDist ' + str(Dist) + ' Speed 120')
        L, R = get_motors()
        PostOdo = odometry(L, R)
        time.sleep(0.1)
        PrevOdo = PostOdo[:]
        PrevOdo[0] = PrevOdo[0] + 1
        while PrevOdo != PostOdo :
            L, R = get_motors()
            PrevOdo = PostOdo[:]
            PostOdo = odometry(L, R)
            time.sleep(0.1)

if __name__ == "__main__":
	# Open the Serial Port.
	global ser
	ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=0.05)
	envia(ser, 'TestMode On')

	envia(ser, 'PlaySound 1')

	envia(ser ,'SetMotor RWheelEnable LWheelEnable')

	global L_ini, R_ini
	

	suma_theta = 0
	x = y = 0

	try:
		i = 0
		L_ini, R_ini = get_motors()
		driveTo(-500, 0)
		envia(ser, 'TestMode Off', 0.2)

		# Close the Serial Port.
		ser.close()
		print "Final"
	except KeyboardInterrupt:
		print "KeyboardInterrupt"
