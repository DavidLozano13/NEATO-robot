# To import the function "envia" from the file "test_NeatoCommands.py"
from test_NeatoCommands import envia
import sys
import serial
import time
from multiprocessing import Process, Queue
import http_viewer
import math
import random

###################### !!! W A R N I N G !!! ########################
# Each group working in the same robot has to chose a different port.
port_web_server = int(sys.argv[1])
#####################################################################
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

def getLDS():
	set('SetLDSRotation On', 1500);
	get('GetLDSScan');
	
	LDS_data = [];
	while ser.inWaiting()>0:
		line = ser.readline();
		line_split = line.split(",");
		if (len(line_split) == 4 and line_split[0].isdigit()):
			#Array ['AngleInDegrees', 'DistInMM', 'errorCode']
			line_content = [line_split[0], line_split[1], line_split[3]];
			LDS_data.append(line_content);
	
	set('SetLDSRotation Off', 100);
   
	return LDS_data;


def get_motors():
	""" Ask to the robot for the current state of the motors. """
	msg = envia(ser, 'GetMotors LeftWheel RightWheel').split('\n')

	# For better understanding see the neato commands PDF.

	L = int(msg[4].split(',')[1])
	R = int(msg[8].split(',')[1])

	return (L, R)

def getLaserValues():
	global speed
	res = [2000,2000,2000,2000,2000,2000,2000,2000,2000,2000]
	msg = getLDS()
	values = [2000 for num in range(360)]
	for value in msg:
		if int(value[1]) > 0:
			values[int(value[0])] = int(value[1])
	# Coger 5 posiciones: 0-36, 37-72, 73-108, 109-144, 145-180
	# Init
	res[0] = values[0]
	res[1] = values[36]
	res[2] = values[72]
	res[3] = values[108]
	res[4] = values[144]
	res[5] = values[180]
	res[6] = values[216]
	res[7] = values[252]
	res[8] = values[288]
	res[9] = values[324]

	for i in range(0,359):
		if i >= 0 and i <= 35:
			# Zona izquierda
			if values[i] < res[0] and values[i] != 0:
				res[0] = values[i]
		if i >= 36 and i <= 71:
			# Zona izquierda central
			if values[i] < res[1] and values[i] != 0:
				res[1] = values[i]
		if i >= 72 and i <= 107:
			# Zona central
			if values[i] < res[2] and values[i] != 0:
				res[2] = values[i]
		if i >= 108 and i <= 143:
			# Zona derecha central
			if values[i] < res[3] and values[i] != 0:
				res[3] = values[i]
		if i >= 144 and i <= 179:
			# Zona derecha
			if values[i] < res[4] and values[i] != 0:
				res[4] = values[i]
		if i >= 180 and i <= 215:
			# Zona izquierda
			if values[i] < res[5] and values[i] != 0:
				res[5] = values[i]
		if i >= 216 and i <= 251:
			# Zona izquierda central
			if values[i] < res[6] and values[i] != 0:
				res[6] = values[i]
		if i >= 252 and i <= 287:
			# Zona central
			if values[i] < res[7] and values[i] != 0:
				res[7] = values[i]
		if i >= 288 and i <= 323:
			# Zona derecha central
			if values[i] < res[8] and values[i] != 0:
				res[8] = values[i]
		if i >= 324 and i <= 359:
			# Zona derecha
			if values[i] < res[9] and values[i] != 0:
				res[9] = values[i]

	

	resfinal = [res[2], res[1], res[0], res[9], res[8]]
	print(resfinal)

	res[0]=res[0]/10
	res[1]=res[1]/10
	res[2]=res[2]/10
	res[8]=res[8]/10
	res[9]=res[9]/10

	print(res)
	distInicial = 200

	speed = 300
	r = random.randrange(2)
	distL = distInicial - (200 - (res[8]+res[9])/2) - (200 - res[0]) * r
	distR = distInicial - (200 - (res[2]+res[1])/2) - (200 - res[0]) * (1-r)

	distL = distL * speed / 100
	distR = distR * speed / 100
	print('SetMotor LWheelDist '+ str(distL) +' RWheelDist ' + str(distR) + ' Speed ' + str(speed))
	envia(ser, 'SetMotor LWheelDist '+ str(distL) +' RWheelDist ' + str(distR) + ' Speed ' + str(speed))
	return res

	#leftMotor.setVelocity(initialVelocity - (centralRightSensorValue + outerRightSensorValue) / 2)
	#rightMotor.setVelocity(initialVelocity - (centralLeftSensorValue + outerLeftSensorValue) / 2 - centralSensorValue)

def odometry(L, R):
	global x
	global y
	global suma_theta
	global L_ini, R_ini
	#Implement the pos integration. Assume initial conditions [0,0,0].
	delta_d = (R+L)/2
	delta_th = (R-L)/243
	#Use global variables, discoment this line
	#global VARIABLES
	new_L, new_R = L - L_ini, R - R_ini

	L_ini = L
	R_ini = R
	suma_theta = (suma_theta+delta_th)
	dx = delta_d*math.cos(suma_theta)
	dy = delta_d*math.sin(suma_theta)
	print (dx,dy,suma_theta)
	x = x + dx
	y = y + dy
	# Return x_word, y_word, theta_word

if __name__ == "__main__":

	r_queue = Queue()
	l_queue = Queue()
	viewer = http_viewer.HttpViewer(port_web_server, l_queue, r_queue)
	print "To open the viewer go to: http:\\\\192.168.100.1:" + str(port_web_server)
	print "To see the log run in a shell the next comnnad: 'tail -f log.txt'"
	print "Press 'Q' to stop the execution."

	# Open the Serial Port.
	global ser
	ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=0.05)
	envia(ser, 'TestMode On')

	envia(ser, 'PlaySound 1')

	envia(ser ,'SetMotor RWheelEnable LWheelEnable')

	global L_ini, R_ini
	L_ini, R_ini = get_motors()

	suma_theta = 0
	x = y = 0

	#envia(ser, 'SetMotor LWheelDist '+ str(100) +' RWheelDist ' + str(100) + ' Speed ' + str(speed))

	try:
		i = 0
		L, R = get_motors()
		while True:
			#L, R = get_motors()
			getLaserValues()
			r_queue.put([(-L/40.0, i), (100,100)])
			l_queue.put([(-R/40.0, i), (200,100)])

			#odometry(L, R)
			time.sleep(0.1)
			i+=60


		envia(ser, 'TestMode Off', 0.2)

		# Close the Serial Port.
		ser.close()
		print "Final"
		viewer.quit()
	except KeyboardInterrupt:
		viewer.quit()
