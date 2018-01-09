# To import the function "envia" from the file "test_NeatoCommands.py"
from test_NeatoCommands import envia
import sys
import serial
import time
from multiprocessing import Process, Queue
import http_viewer
import math

###################### !!! W A R N I N G !!! ########################
# Each group working in the same robot has to chose a different port.
port_web_server = int(sys.argv[1])
#####################################################################
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
	global L_ini, R_ini
	#Implement the pos integration. Assume initial conditions [0,0,0].
	delta_d = (R+L)/2
	delta_th = (L-R)/243
	#Use global variables, discoment this line
	#global VARIABLES
	new_L, new_R = L - L_ini, R - R_ini
	
	L_ini = L
	R_ini = R
	x = x + delta_d*math.cos(suma_theta)
	y = y + delta_d*math.sin(suma_theta)
	suma_theta = (suma_theta+delta_th)%(2*math.pi)
	print(new_L, new_R, new_L/new_R)
	print (x,y,suma_theta)
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
	
	speed = 100	# en mm/s
	envia(ser, 'SetMotor LWheelDist '+ str(5000) +' RWheelDist ' + str(5000) + ' Speed ' + str(speed))


	try:
		i = 0
		L, R = get_motors()
		while True:
			L, R = get_motors()
			r_queue.put([(-L/40.0, i), (100,100)])
			l_queue.put([(-R/40.0, i), (200,100)])

			odometry(L, R)
			time.sleep(0.1)
			i+=60
		

		envia(ser, 'TestMode Off', 0.2)

		# Close the Serial Port.
		ser.close()      

		print "Final"
		viewer.quit()
	except KeyboardInterrupt:
		viewer.quit()
	