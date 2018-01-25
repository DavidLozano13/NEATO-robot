# To import the function "envia" from the file "test_NeatoCommands.py"
from test_NeatoCommands import envia
import sys
import serial
import time
from multiprocessing import Process, Queue
import math
import random

def set(message, timeInMs):
    #print "SET - Message: %s, SleepTimeInMs: %f" %(message, timeInMs);
    ser.write(message+'\r'+'\n');
    time.sleep(abs(timeInMs/1000));

def get(message):
    #print "GET - Message: %s" %message;
    ser.write(message+'\r'+'\n');

def getLDS():
	msg = envia(ser, 'GetLDSScan',0.2,False)
	var = []
	for line in msg.split('\r\n')[2:362]:
		s = line.split(',')
		var.append([s[0], s[1], s[2], s[3]])
	return var

def getLaserValues():
	global speed
	global difDestino
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

	res[0]=res[0]/10
	res[1]=res[1]/10
	res[2]=res[2]/10
	res[8]=res[8]/10
	res[9]=res[9]/10

	distInicial = 200

	distL = distInicial - (distInicial - (res[8]+res[9])/2) - (distInicial - res[0])
	distR = distInicial - (distInicial - (res[2]+res[1])/2) - (distInicial - res[0])
	
	print('=============================')
	print('diferencia: '+str(difDestino))
	speed = 150
	if difDestino > 0:
		print('deberia girar a la izquierda')
		if (res[1] > 50 and res[2] > 20):
			distR = distR * 1.25
			distL = distL * 0.75
			print('puedo girar a la izquierda!')
	elif difDestino < 0:
		print('deberia girar a la derecha')
		if (res[9] > 50 and res[8] > 20):
			distL = distL * 1.25
			distR = distR * 0.75
			print('puedo girar a la derecha!')
	
	distL = distL * speed / 100
	distR = distR * speed / 100
	difDestino = difDestino + distL - distR
	#print('SetMotor LWheelDist '+ str(distL) +' RWheelDist ' + str(distR) + ' Speed ' + str(speed))
	envia(ser, 'SetMotor LWheelDist '+ str(distL) +' RWheelDist ' + str(distR) + ' Speed ' + str(speed))
	return res

if __name__ == "__main__":

	r_queue = Queue()
	l_queue = Queue()
	# Open the Serial Port.
	global ser
	ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=0.05)
	envia(ser, 'TestMode On')

	envia(ser, 'PlaySound 1')

	envia(ser ,'SetMotor RWheelEnable LWheelEnable')
	envia(ser, 'SetLDSRotation On',0.2,False)

	difDestino = 0
	#envia(ser, 'SetMotor LWheelDist '+ str(100) +' RWheelDist ' + str(100) + ' Speed ' + str(speed))

	try:
		while True:
			getLaserValues()
			time.sleep(0.1)

		envia(ser, 'TestMode Off', 0.2)

		# Close the Serial Port.
		ser.close()
		print "Final"
	except KeyboardInterrupt:
		envia(ser, 'SetLDSRotation Off',0.2,False)
		print "Final"
