# To import the function "envia" from the file "test_NeatoCommands.py"
from test_NeatoCommands import envia

import serial
import time
import math


x=0
y=0
suma_theta=0

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
	#Implement the pos integration. Assume initial conditions [0,0,0].
	delta_d = (R+L)/2
	delta_th = (R-L)/243
	#Use global variables, discoment this line
	#global VARIABLES
	new_L, new_R = L - L_ini, R - R_ini
	x += delta_d*math.cos(suma_theta)
	y += delta_d*math.sin(suma_theta)
	suma_theta = (suma_theta+delta_th)%(2*math.pi)
	print(new_L, new_R, new_L/new_R)
	print(x,y,suma_theta)
	# Return x_word, y_word, theta_word

if __name__ == "__main__":
	# Open the Serial Port.
	global ser
	ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=0.05)
	envia(ser, 'TestMode On')

	envia(ser, 'PlaySound 1')

	envia(ser ,'SetMotor RWheelEnable LWheelEnable')

	global L_ini, R_ini
	L_ini, R_ini = get_motors()
	
	speed = 100	# en mm/s
	envia(ser, 'SetMotor LWheelDist '+ str(5519) +' RWheelDist ' + str(7046) + ' Speed ' + str(speed))
	
	while True:
		L, R = get_motors()
		odometry(L, R)
		time.sleep(0.1)
	

	envia(ser, 'TestMode Off', 0.2)

	# Close the Serial Port.
	ser.close()      

	print "Final"