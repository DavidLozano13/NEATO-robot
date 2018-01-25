# To import the function "envia" from the file "test_NeatoCommands.py"
from test_NeatoCommands import envia
import sys
import serial
import time
from multiprocessing import Process, Queue
import math
import numpy

x=0
y=0
suma_theta=0
distance_weels_mid = 121.5
distance_robot = 318
speed = 125


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
	L, R = get_motors()
	odom = odometry(L,R)
	x_go = X - odom[0]
	y_go = Y - odom[1]

	angleRest = numpy.arctan2(y_go,x_go)
	if odom[2] - angleRest > 2*math.pi - (odom[2] - angleRest):
		angle = - (2 * math.pi - (odom[2] - angleRest))
	else: 
		angle = odom[2] - angleRest

	envia(ser, 'SetMotor LWheelDist '+ str(angle*distance_weels_mid) +' RWheelDist ' + str(-angle*distance_weels_mid) + ' Speed '+str(speed))
	time.sleep(abs((angle*distance_weels_mid)/speed))
	
	Dist = numpy.sqrt(x_go*x_go + y_go*y_go)
	envia(ser, 'SetMotor LWheelDist '+ str(Dist) +' RwheelDist ' + str(Dist) + ' Speed '+str(speed))
	time.sleep(Dist/speed)

	envia(ser, 'SetMotor LWheelDist '+ str(-angle*distance_weels_mid) +' RWheelDist ' + str(angle*distance_weels_mid) + ' Speed '+str(speed))
	time.sleep(abs((angle*distance_weels_mid)/speed))

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
		
		driveTo(800, 800)
		envia(ser, 'TestMode Off', 0.2)

		# Close the Serial Port.
		ser.close()
		print "Final"
	except KeyboardInterrupt:
		print "KeyboardInterrupt"
