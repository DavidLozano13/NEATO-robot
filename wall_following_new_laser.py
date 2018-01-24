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


def get_laser():
    msg = envia(ser, 'GetLDSScan',0.2,False)
    var = []
    for line in msg.split('\r\n')[2:362]:
        s = line.split(',')
        var.append([s[0], s[1], s[2], s[3]])
    return var


def get_5sensor (laser):
    sensor = []
    for i in range (0,5):
        sensor.append(dist_max)
        for j in range (-60 + i*24, -60 + 24 + i*24):
            if int(laser[j][3]) == 0:
                #print laser[j][1],' < ',sensor[i]
                if (int(laser[j][1]) < sensor[i]):
                    sensor[i] = int(laser[j][1])

    print(sensor)

    return sensor

if __name__ == "__main__":
	perimeterRobot = 2*math.pi*24.3/4
	# Open the Serial Port.
	global ser
    ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=0.05)
    print 'INI: SerialPort -> on'
    envia(ser, 'TestMode On',0.2)
    envia(ser, 'PlaySound 1')
    print 'INI: TestMode -> on'
    envia(ser, 'SetMotor RWheelEnable LWheelEnable')
    print 'INI: SetMotor -> on'
    envia(ser, 'SetLDSRotation On',0.2,False)

	try:

		var = get_5sensor(get_laser())
		#Acercarse al muro
		while var(0) > 60:
			envia(ser, 'SetMotor LWheelDist 100 RWheelDist 100 Speed 50')
			var = get_5sensor(get_laser())

		#Girar para tener el muro a la derecha
		while var(8) > 40:
			envia(ser, 'SetMotor LWheelDist 0 RWheelDist 180 Speed 100')
			var = get_5sensor(get_laser())

		while True:
			#muro delante
			if (var(0)<30)
				envia(ser, 'SetMotor LWheelDist 0 RWheelDist 'perimeterRobot' Speed 100')
				time.sleep(0.1)
			#cerca del muro
			if var(8) < 30:
				envia(ser, 'SetMotor LWheelDist 0 RWheelDist 100 Speed 100')
				time.sleep(0.1)
	        #lejos el muro
			elif var(8) > 30:
				envia(ser, 'SetMotor LWheelDist 100 RWheelDist 0 Speed 100')
				time.sleep(0.1)
			else
				envia(ser, 'SetMotor LWheelDist 100 RWheelDist 100 Speed 50')

			var = get_5sensor(get_laser())
		


		envia(ser, 'TestMode Off', 0.2)

		# Close the Serial Port.
		ser.close()
		print "Final"
	except KeyboardInterrupt:
		print "Final"
