# To import the function "envia" from the file "test_NeatoCommands.py"
from test_NeatoCommands import envia
import sys
import serial
import time
from multiprocessing import Process, Queue
import math
import random

###################### !!! W A R N I N G !!! ########################
# Each group working in the same robot has to chose a different port.
port_web_server = int(sys.argv[1])
#####################################################################


def set(message, timeInMs):
    #print "SET - Message: %s, SleepTimeInMs: %f" %(message, timeInMs);
    ser.write(message+'\r'+'\n');
    time.sleep(abs(timeInMs/1000));

def get(message):
    #print "GET - Message: %s" %message;
    ser.write(message+'\r'+'\n');

def getLDS():
	res = envia(ser, 'GetLDSScan',0.2,False)
	var = []
	for line in res.split('\r\n')[2:362]:
		l = line.split(',')
		var.append([l[0], l[1], l[2], l[3]])
	return var

def getLaserValues():
	global speed
	global difDestino
	global resfinal
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

	resfinal = [res[2], res[1], res[0], res[9], res[8]]
	print(resfinal)
	
	return resfinal

	#leftMotor.setVelocity(initialVelocity - (centralRightSensorValue + outerRightSensorValue) / 2)
    #rightMotor.setVelocity(initialVelocity - (centralLeftSensorValue + outerLeftSensorValue) / 2 - centralSensorValue)


if __name__ == "__main__":

	# Open the Serial Port.
	global ser
	ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=0.05)
	envia(ser, 'TestMode On')

	envia(ser, 'PlaySound 1')

	envia(ser ,'SetMotor RWheelEnable LWheelEnable')

	envia(ser, 'SetLDSRotation On',0.2,False)

	try:
		#Acercarse al muro
		getLaserValues()
		while resfinal[2] > 60:
			if resfinal[2] < 100:
				envia(ser, 'SetMotor LWheelDist 100 RWheelDist 100 Speed 50')
			else:
				envia(ser, 'SetMotor LWheelDist 200 RWheelDist 200 Speed 100')			
			getLaserValues()
		
		#Girar para tener el muro a la derecha
		if resfinal[0] >= resfinal[4]:
			while resfinal[4] > 40:
				envia(ser, 'SetMotor LWheelDist 0 RWheelDist 180 Speed 100')
				getLaserValues()
			while True:
				#muro delante
				if resfinal[2] < 50:
					envia(ser, 'SetMotor LWheelDist 0 RWheelDist 180 Speed 100')
				#cerca del muro
				elif resfinal[4] < 30:	
					envia(ser, 'SetMotor LWheelDist 20 RWheelDist 50 Speed 50')
		        #lejos del muro
				elif resfinal[4] > 40:
					envia(ser, 'SetMotor LWheelDist 50 RWheelDist 20 Speed 50')
				else:
					correccion = (resfinal[3] - resfinal[4])
					print(str(correccion))
					if resfinal[2] < 100:
						envia(ser, 'SetMotor LWheelDist ' + str(85 + correccion) + ' RWheelDist 100 Speed 50')
					else:
						envia(ser, 'SetMotor LWheelDist ' + str(185 + correccion) + ' RWheelDist 200 Speed 100')
						
				getLaserValues()
		#Girar para tener el muro a la izquierda
		else:
			while resfinal[0] > 40:
				envia(ser, 'SetMotor LWheelDist 180 RWheelDist 0 Speed 100')
				getLaserValues()
			while True:
				#muro delante
				if resfinal[2] < 50:
					envia(ser, 'SetMotor LWheelDist 180 RWheelDist 0 Speed 100')
				#cerca del muro
				elif resfinal[0] < 30:	
					envia(ser, 'SetMotor LWheelDist 50 RWheelDist 20 Speed 50')
		        #lejos del muro
				elif resfinal[0] > 40:
					envia(ser, 'SetMotor LWheelDist 20 RWheelDist 50 Speed 50')
				else:
					correccion = (resfinal[1] - resfinal[0])
					print(str(correccion))
					if resfinal[2] < 100:
						envia(ser, 'SetMotor LWheelDist 100 RWheelDist ' + str(85 + correccion) + ' Speed 50')
					else:
						envia(ser, 'SetMotor LWheelDist 200 RWheelDist ' + str(185 + correccion) + ' Speed 100')
				getLaserValues()
			
		envia(ser, 'TestMode Off', 0.2)

		# Close the Serial Port.
		ser.close()
		print "Final"
	except KeyboardInterrupt:
		envia(ser, 'SetLDSRotation Off',0.2,False)
		print "Final"
