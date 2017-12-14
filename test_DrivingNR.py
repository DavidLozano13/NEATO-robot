#!/usr/bin/python
#coding: utf8

"""
Imports
"""
import time

import serial

"""
Imports de Teclado
"""
import os
import sys, tty, termios
from select import select

# To import the function "envia" from the file "test_NeatoCommands.py"
from test_NeatoCommands import envia

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:

        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)

    finally:

        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
	print ch
    return ch



# Llamada a la funcion main
if __name__ == '__main__':

	global ser
	# Open the Serial Port.
	ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=1)

	envia(ser,'TestMode On', 0.2)

	envia(ser,'PlaySound 1', 0.3)

	envia(ser,'SetMotor RWheelEnable LWheelEnable', 0.2)

	# Parametros Robot.
	S = 121.5		# en mm
	distancia_L = 0	# en mm
	distancia_R = 0	# en mm
	speed = 0 		# en mm/s
	tita_dot = 0
	tiempo = 20		
	direccion = 0

	print "########################"
	print "Speed = " + str(speed)
	print "Tita_dot = " + str(tita_dot)

	if direccion == 0:
		print "Direction: fordward."
	else:
		print "Direction: backward."

	print "q to exit."
	print "########################"

	# Tecla a leer.
	tecla = ''
	comando = ''
	
	while tecla != "q":

		# Leemos la tecla.
		print "Write command: "       
		tecla = getch()

		if tecla == '8' or tecla == '2':

			if tecla == '8':
				speed = speed + 50
			else:
				speed = speed - 50

			if speed >= 0:
				direccion = 0
			else:
				direccion = 1

			if speed == 0:

				envia(ser,'SetMotor LWheelDisable RWheelDisable', 0.2)
				envia(ser,'SetMotor RWheelEnable LWheelEnable', 0.2)

			else:
				distancia_R = (((speed * pow(-1, direccion) ) + (S * tita_dot)) * tiempo) * pow(-1, direccion)
				distancia_L = (((speed * pow(-1, direccion) ) + (-S * tita_dot)) * tiempo) * pow(-1, direccion)

				comando = 'SetMotor LWheelDist ' + str(distancia_L) + ' RWheelDist ' + str(distancia_R) + ' Speed ' + str(speed * pow(-1, direccion))
				envia(ser,comando, 0.2)

		elif tecla == '4' or tecla == '6':

			if tecla == '4':
				tita_dot = tita_dot + (3.1415/10)
			else:
				tita_dot = tita_dot - (3.1415/10)

			distancia_R = (((speed * pow(-1, direccion) ) + (S * tita_dot)) * tiempo) * pow(-1, direccion)
			distancia_L = (((speed * pow(-1, direccion) ) + (-S * tita_dot)) * tiempo) * pow(-1, direccion)

			comando = 'SetMotor LWheelDist ' + str(distancia_L) + ' RWheelDist ' + str(distancia_R) + ' Speed ' + str(speed * pow(-1, direccion))
			envia(ser,comando, 0.2)

		elif tecla == '5':

			direccion = 0
			speed = 0
			tita_dot = 0
			distancia_L = 0
			distancia_R = 0

			envia(ser,'SetMotor LWheelDisable RWheelDisable', 0.2)
			envia(ser,'SetMotor RWheelEnable LWheelEnable', 0.2)

		if tecla == '8' or tecla == '2' or tecla == '6' or tecla == '4' or tecla == '5':
			
			#print "\n########################"
			#print 'Comando enviado: ' + comando
			print "########################"
			print "########################"
			print "Speed = " + str(speed)
			print "Tita_dot = " + str(tita_dot)

			if direccion == 0:
				print "Direction: fordward."
			else:
				print "Direction: backward."
			print "########################"