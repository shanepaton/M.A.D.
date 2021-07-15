# Mounted Assistant Device
# The M.A.D. MK.1
# BY SHANE PATON
import socket
import sys
import os
import time
import threading
from datetime import datetime
import RPi.GPIO as GPIO
from RPLCD.i2c import CharLCD

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip = s.getsockname()[0]
s.close()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# Screen initialization
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
			  cols=16, rows=2, dotsize=8,
			  charmap='A02',
			  auto_linebreaks=True,
			  backlight_enabled=True)

# Setup Pins
GPIO.setup(23, GPIO.OUT)
GPIO.setup(16, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(21, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(4, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, GPIO.PUD_UP)

# System Variables
screenState = 0
listState = 0
listLimit = 7
drawBrewHud = False

# Program Variables
buttonValue = 0
buttonState = False
brewSoftList = []
brewListPos = 0

# Custom Charecters
buttonUnpressLeftChar = (
	0x00,
	0x03,
	0x04,
	0x07,
	0x04,
	0x04,
	0x03,
	0x00
)

buttonUnpressRightChar = (
	0x00,
	0x18,
	0x04,
	0x1C,
	0x04,
	0x04,
	0x18,
	0x00
)

buttonPressedLeftChar = (
	0x00,
	0x00,
	0x00,
	0x03,
	0x07,
	0x07,
	0x03,
	0x00
)

buttonpPressedRightChar = (
	0x00,
	0x00,
	0x00,
	0x18,
	0x1C,
	0x1C,
	0x18,
	0x00
)
arrowLeftChar = (
	0x00,
	0x04,
	0x08,
	0x1F,
	0x08,
	0x04,
	0x00,
	0x00
)

arrowRightChar = (
	0x00,
	0x04,
	0x02,
	0x1F,
	0x02,
	0x04,
	0x00,
	0x00
)

# Charecter Creation
lcd.create_char(0, buttonUnpressLeftChar)
lcd.create_char(1, buttonUnpressRightChar)
lcd.create_char(2, buttonPressedLeftChar)
lcd.create_char(3, buttonpPressedRightChar)
lcd.create_char(4, arrowLeftChar)
lcd.create_char(5, arrowRightChar)

# Buzzer setup
global Buzz
Buzz = GPIO.PWM(23, 440)
Buzz.start(50)
def startupSound():
	startupJingle = [
		208, 233, 311
	]
	for i in range(0, len(startupJingle)):
		Buzz.ChangeFrequency(startupJingle[i])
		time.sleep(0.1)
	Buzz.stop()

# Clears the screen
def cls():
	lcd.clear()

# Prints strings letter by letter
def printOBO(str):
	if len(str) > 17:
		raise Exception("Error attempted to print more than 16 charecters")
	for char in str:
		lcd.write_string(char)
		sys.stdout.flush()
		time.sleep(0.075)

# Gets the full day of the week
def getWeekday(full):

	if full:
		if datetime.today().weekday() == 0:
			return "MONDAY"
		if datetime.today().weekday() == 1:
			return "TUESDAY"
		if datetime.today().weekday() == 2:
			return "WEDNESDAY"
		if datetime.today().weekday() == 3:
			return "THURSDAY"
		if datetime.today().weekday() == 4:
			return "FRIDAY"
		if datetime.today().weekday() == 5:
			return "SATURDAY"
		if datetime.today().weekday() == 6:
			return "SUNDAY"
	if not full:
		if datetime.today().weekday() == 0:
			return "MON"
		if datetime.today().weekday() == 1:
			return "TUE"
		if datetime.today().weekday() == 2:
			return "WED"
		if datetime.today().weekday() == 3:
			return "THU"
		if datetime.today().weekday() == 4:
			return "FRI"
		if datetime.today().weekday() == 5:
			return "SAT"
		if datetime.today().weekday() == 6:
			return "SUN"

# Scans drive for Brewsoft programs
def scanForBrew():
	global drawBrewHud
	brewSoftList.clear()
	for directory, subdirectories, files in os.walk('/media/pi/PROGRAM/programs/'):
		for file in files:
			brewSoftList.append(file.replace('.py', ''))
	print(brewSoftList)
	if len(brewSoftList) == 0:
		brewSoftList.clear()
		brewSoftList.append('----')
		print(brewSoftList)
		drawBrewHud = True

# Function for Brewsoft devs to end their program
def endBrewProgram():
	global drawBrewHud
	drawBrewHud = True

# Button beeps for menus [ thread function ]
def buttonBuzzTask():
	Buzz.start(50)
	Buzz.ChangeFrequency(208)
	time.sleep(0.1)
	Buzz.stop()

# Home button
def homeReleased(pin):
	global screenState
	print("home")
	if screenState == 0:
		screenState = 1
	elif screenState == 1:
		screenState = 0
	else:
		screenState = 0

# Left Button
def leftReleased(pin):
	global listState
	global listLimit
	global screenState
	global brewListPos

	if screenState == 1:
		if listState >= 1:
			listState -= 1
			thread = threading.Thread(target=buttonBuzzTask)
			thread.start()
			print("left " + str(listState))
	if screenState == 11:
		if brewListPos >= 1:
			brewListPos -= 1
			thread = threading.Thread(target=buttonBuzzTask)
			thread.start()

# Right Button
def rightReleased(pin):
	global listState
	global listLimit
	global screenState
	global brewListPos
	global brewSoftList

	if screenState == 1:
		if listState <= listLimit - 1:
			listState += 1
			thread = threading.Thread(target=buttonBuzzTask)
			thread.start()
	if screenState == 11:
		if brewListPos <= len(brewSoftList) - 2:
			brewListPos += 1
			thread = threading.Thread(target=buttonBuzzTask)
			thread.start()

# Select Button
def selectButton(pin):
	global listState
	global listLimit
	global screenState
	global buttonState
	global drawBrewHud

	if GPIO.input(22):
		if screenState == 16:

			buttonState = True
	else:

		if screenState == 16:
			global buttonValue
			buttonState = False
			buttonValue += 1

		if screenState == 1:
			if listState == 0:
				screenState = 0
			if listState == 1:
				screenState = 2
			if listState == 2:
				screenState = 16
			if listState == 3:
				screenState = 17
			if listState == 4:
				screenState = 18
			if listState == 5:
				screenState = 9
			if listState == 6:
				screenState = 8
			if listState == 7:
				screenState = 11
		if screenState == 11:
			if len(brewSoftList) > 0 and '----' in brewSoftList[0]:
				scanForBrew()
			if drawBrewHud == True:
				drawBrewHud = False
			else:
				drawBrewHud = True

# Event Listeners
GPIO.add_event_detect(16, GPIO.RISING, callback=homeReleased)
GPIO.add_event_detect(21, GPIO.RISING, callback=leftReleased, bouncetime=100)
GPIO.add_event_detect(4, GPIO.RISING, callback=rightReleased, bouncetime=100)
GPIO.add_event_detect(22, GPIO.BOTH, callback=selectButton, bouncetime=100)

# Startup
def Startup(doDo):
	startupSound()
	if doDo == True:
		lcd.cursor_pos = (0, 0)
		printOBO('THE M.A.D.  MK.1')
		lcd.cursor_pos = (1, 0)
		printOBO(' BY SHANE PATON ')
		time.sleep(2.1)
		cls()
		lcd.cursor_pos = (0, 0)
		printOBO('FIRMWARE VERSION')
		lcd.cursor_pos = (1, 0)
		printOBO('1.0.2 (C)2021 SP')
		time.sleep(1.9)
		cls()
		lcd.cursor_pos = (0, 0)
		printOBO('  INITIALIZING  ')
		lcd.cursor_pos = (1, 0)
		printOBO(' SYSTEM STARTUP ')
		time.sleep(2.1)
		cls()
		lcd.cursor_pos = (0, 0)
		printOBO('   LOADING...   ')
		lcd.cursor_pos = (1, 0)
		printOBO('POWER MANAGEMENT')
		time.sleep(1.4)
		cls()
		lcd.cursor_pos = (0, 0)
		printOBO('   LOADING...   ')
		lcd.cursor_pos = (1, 0)
		printOBO('  VOLT MONITOR  ')
		time.sleep(0.9)
		cls()
		lcd.cursor_pos = (0, 0)
		printOBO('   LOADING...   ')
		lcd.cursor_pos = (1, 0)
		printOBO(' INTERNAL CLOCK ')
		time.sleep(2)
		cls()
		lcd.cursor_pos = (0, 0)
		printOBO('   LOADING...   ')
		lcd.cursor_pos = (1, 0)
		printOBO('DIAGNOSTIC PANEL')
		time.sleep(2.2)
		cls()
		lcd.cursor_pos = (0, 0)
		printOBO('   LOADING...   ')
		lcd.cursor_pos = (1, 0)
		printOBO(' MENU UTILITIES ')
		time.sleep(2.3)
		cls()
		lcd.cursor_pos = (0, 0)
		printOBO('   LOADING...   ')
		lcd.cursor_pos = (1, 0)
		printOBO(' SYSTEM  ADDONS ')
		time.sleep(1.2)
		cls()
		lcd.cursor_pos = (0, 0)
		printOBO('   LOADING...   ')
		lcd.cursor_pos = (1, 0)
		printOBO('  INPUT SYSTEM  ')
		time.sleep(0.9)
		cls()
		lcd.cursor_pos = (0, 0)
		printOBO('    COMPLETE    ')
		lcd.cursor_pos = (1, 0)
		printOBO('HAVE A GOOD DAY!')
		time.sleep(1)
		cls()
		scanForBrew()

	if doDo == False:
		scanForBrew()

# HOME program - The default program that runs on startup [ shows the date and time ].
def PROGRAM_HOME():
	lcd.cursor_pos = (0, 0)
	lcd.write_string("    " + datetime.now().strftime("%H:%M:%S") + "    ")
	lcd.cursor_pos = (1, 0)
	lcd.write_string(getWeekday(False) + " | " +
					 datetime.today().strftime("%d/%m/%Y"))

# LIST program - Shows all programs and selects which one the user wants to run.
def PROGRAM_LIST(page):
	if page == 0:
		lcd.cursor_pos = (0, 0)
		lcd.write_string("--   [HOME]   --")
		lcd.cursor_pos = (1, 0)
		lcd.write_string("    THE HOME    ")

	elif page == 1:
		lcd.cursor_pos = (0, 0)
		lcd.write_string("--   [DATE]   --")
		lcd.cursor_pos = (1, 0)
		lcd.write_string(" SHOWS THE DATE ")

	elif page == 2:
		lcd.write_string("--   [PUSH]   --")
		lcd.write_string("PUSH BUTTON GAME")

	elif page == 3:
		lcd.write_string("--   [HALF]   --")
		lcd.write_string(" HALF-LIFE JOKE ")

	elif page == 4:
		lcd.write_string("--   [CAKE]   --")
		lcd.write_string("PORTAL CAKE JOKE")

	elif page == 5:
		lcd.write_string("--   [INFO]   --")
		lcd.write_string("SHOW SYSTEM INFO")

	elif page == 6:
		lcd.write_string("--   [FIRM]   --")
		lcd.write_string("DISPLAY FIRMWARE")

	elif page == 7:
		lcd.write_string("--   [BREW]   --")
		lcd.write_string("CUSTOM SOFTWARE!")

	else:
		lcd.write_string("--    ----    --")
		lcd.write_string("[----]    [----]")

# DATE program - Program that shows the date.
def PROGRAM_DATE():
	lcd.cursor_pos = (0, 0)
	lcd.write_string("--    DATE    --")
	lcd.cursor_pos = (1, 0)
	lcd.write_string(getWeekday(False) + " | " +
					 datetime.today().strftime("%d/%m/%Y"))

# BREW program - Load custom software from a drive
def PROGRAM_BREW():
	scanForBrew()
	if drawBrewHud:
		scanForBrew()
		lcd.cursor_pos = (0, 0)
		lcd.write_string("==  BREWSOFT  ==")
		lcd.cursor_pos = (1, 0)
		lcd.write_string(
			"\x04" + str(brewSoftList[brewListPos]).center(14) + "\x05")
	else:
		scanForBrew()
		if len(brewSoftList) > 0 and not '----' in brewSoftList[0]:
			exec(open('/media/pi/PROGRAM/programs/' + brewSoftList[brewListPos] + '.py').read())

# FIRM program - Shows system firmware
def PROGRAM_FIRM():
	lcd.cursor_pos = (0, 0)
	lcd.write_string("--  FIRMWARE  --")
	lcd.cursor_pos = (1, 0)
	lcd.write_string(" REVSION  1.0.2 ")

# INFO program - Displays the OS version running on the M.A.D.
def PROGRAM_INFO():
	lcd.cursor_pos = (0, 0)
	lcd.write_string("--    INFO    --")
	lcd.cursor_pos = (1, 0)
	lcd.write_string("SYSTEM OS: 1.0.2")

# HALF program - Little Valve easter egg program, displays HP and SUIT charge.
def PROGRAM_SUIT():
	lcd.cursor_pos = (0, 0)
	lcd.write_string("HP : 100        ")
	lcd.cursor_pos = (1, 0)
	lcd.write_string("SU:  100        ")

# CAKE program - Little Valve easter egg program, displays the "cake is a lie" quote from the Portal series.
def PROGRAM_CAKE():
	lcd.cursor_pos = (0, 0)
	lcd.write_string("    The Cake    ")
	lcd.cursor_pos = (1, 0)
	lcd.write_string("    is a lie    ")

# PUSH program - Button pusher program!
def PROGRAM_PUSH():
	global buttonState
	lcd.cursor_pos = (0, 0)
	lcd.write_string(str(buttonValue).zfill(16))
	lcd.cursor_pos = (1, 0)
	if not buttonState:
		lcd.write_string("       \x02\x03       ")
	else:
		lcd.write_string("       \x00\x01       ")

# TEST program - A test program.
def PROGRAM_TEST():
	cls()
	print("      TEST      ")
	print(" This is a test ")
	cls()

# List of programs - Used for state management in the main loop
programsList = {
	"HOME": 0,
	"LIST": 1,
	"DATE": 2,
	"FIRM": 8,
	"INFO": 9,
	"PUSH": 16,
	"HALF": 17,
	"CAKE": 18,
	"BREW": 11,
	"TEST": 999,
}

if __name__ == '__main__':
	try:
		# Does startup
		Startup(False)
		while True:
			if screenState == programsList["HOME"]:
				PROGRAM_HOME()
			if screenState == programsList["DATE"]:
				PROGRAM_DATE()
			if screenState == programsList["LIST"]:
				PROGRAM_LIST(listState)
			if screenState == programsList["FIRM"]:
				PROGRAM_FIRM()
			if screenState == programsList["INFO"]:
				PROGRAM_INFO()
			if screenState == programsList["PUSH"]:
				PROGRAM_PUSH()
			if screenState == programsList["HALF"]:
				PROGRAM_SUIT()
			if screenState == programsList["BREW"]:
				PROGRAM_BREW()
			if screenState == programsList["CAKE"]:
				PROGRAM_CAKE()
			if screenState == programsList["TEST"]:
				PROGRAM_TEST()
	except KeyboardInterrupt:
		pass
	finally:
		lcd.clear()
		cls()
		GPIO.cleanup()
