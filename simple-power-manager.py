#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from commands import getoutput,getstatusoutput

import pyxhook
import time
import os
import dbus
import threading

inactiveTime=time.time()
actualBright=-1
flagBright=False
flagLow=False
flagCritic=False
graphicCards=[]
settings=[["powerButton",1],["keyBright",1],["lidScreen",1],["screensaverOnSuspend",1],["notify",1],["batteryLow",20],["batteryCritic",5],["dynamicBright",0],["unplugInactiveTime",5],["unplugInactiveBright",10],["plugInactiveTime",30],["plugInactiveBright",20],["suspendInactivity",30],["suspendInactivityTime",1800]]

KBD = "269025027"
KBU = "269025026"
KSD = "269025066"
SLD = "269025201"

def getSettings():
	while(True):
		try:
			global settings
			#configFile=open(os.environ['HOME']+"/.config/simple-power-manager/config.conf","r")
			configFile=open("/home/kirbylife/.config/simple-power-manager/config.conf","r")
			config=configFile.read()
			configFile.close()
			config=config.split("\n")
			for c in range(len(config)):
				config[c]=config[c].split("=")
			for c in settings:
				for f in config:
					if c[0]==f[0]:
						c[1]=f[1]
						break
			time.sleep(20)
		except:
			configFile=open(os.environ['HOME']+"/.config/simple-power-manager/config.conf","w")
			for c in settings:
				configFile.write(c[0]+"="+str(c[1])+"\n")
			configFile.close()
			getSettings()

def getACAdapter():
	return getoutput("cat /sys/class/power_supply/ACAD/online") == "1"
	
def getBatteryPercent():
	energyNow=int(getoutput("cd /sys/class/power_supply/BAT* && cat energy_now"))
	energyFull=int(getoutput("cd /sys/class/power_supply/BAT* && cat energy_full"))
	
	return int(energyNow*100/energyFull)

def resetTime(event=None):
	global inactiveTime,graphicCards,actualBright,flagBright
	if flagBright:
		for c in graphicCards:
			changeBright(True,c,actualBright)
		flagBright=False
	inactiveTime=time.time()

def suspend(order,ssorder):
	bus=dbus.SystemBus()
	login1Proxy = bus.get_object('org.freedesktop.login1','/org/freedesktop/login1')
	login1 = dbus.Interface(login1Proxy,'org.freedesktop.login1.Manager')
	if ssorder=="1" :
		getoutput("xdg-screensaver lock")
	if order=="1" :
		login1.Suspend(True)
	elif order=="2" :
		login1.Hibernate(True)

def changeBright(value,dir,percent=-1):
	max=int(getoutput("cat /sys/class/backlight/"+dir+"/max_brightness"))
	current=int(getoutput("cat /sys/class/backlight/"+dir+"/actual_brightness"))
	if percent != -1:
		current=percent*max/100
	else:
		if value:
			if current<max :
				current=current+(5*max/100)%max
		else:
			if current>0 :
				current=current-(5*max/100)
				if current<0 :
					current=0
	os.system("sudo echo "+str(current)+" > /sys/class/backlight/"+dir+"/brightness")
	return "2"

def kbevent(event):
	global running,settings,KBD,KBU,KSD,SLD,graphicCards,actualBright
	resetTime()
	key = str(event.Key)
	if KBD in key and settings[1][1]=="1":
		for c in graphicCards:
			actualBright=changeBright(False,c)
	elif KBU in key and settings[1][1]=="1":
		for c in graphicCards:
			actualBright=changeBright(True,c)
	elif KSD in key and settings[0][1]!="0":
		suspend(settings[0][1])
	elif SLD in key and settings[2][1]!="0":
		suspend(settings[2][1],settings[3][1])

def main(args):
	global settings,actualBright,graphicCards,inactiveTime,flagBright
	threadSettings=threading.Thread(target=getSettings)
	hookman = pyxhook.HookManager()
	hookman.KeyDown = kbevent
	hookman.KeyUp=hookman.MouseAllButtonsDown=hookman.MouseAllButtonsUp=hookman.MouseMovement=resetTime
	hookman.HookKeyboard()
	hookman.HookMouse()
	threadSettings.start()
	hookman.start()
	graphicCards=getoutput("ls /sys/class/backlight").split("\n")
	while True:
		currentTime = time.time()-inactiveTime
		if settings[7][1]=="1":
			if(getACAdapter()):
				options=[8,9]
			else:
				options=[10,11]
			print(options)
			if int(currentTime)>=int(settings[options[0]][1]):
				#print (1)
				if flagBright == False:
					for c in graphicCards:
						changeBright(True,c,int(settings[options[1]][1]))
					flagBright = True
					
		if settings[12][1]=="1":
			if int(currentTime) >= int(settings[13][1]):
				suspend("1",settings[3][1])
		
		if settings[4][1]=="1":
			None
				
		time.sleep(0.1)

	hookman.cancel()

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))

