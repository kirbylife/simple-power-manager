#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from commands import getoutput,getstatusoutput

import pyxhook
import time
import os
import dbus

inactiveTime=time.time()
settings=[["powerButton",1],["keyBright",1],["lidScreen",1],["screensaverOnSuspend",1],["notify",1],["batteryLow",20],["batteryCritic",5],["dynamicBright",0],["unplugInactiveTime",5],["unplugInactiveBright",10],["plugInactiveTime",30],["plugInactiveBright",20],["suspendTime",30]]

KBD = "269025027"
KBU = "269025026"
KSD = "269025066"
SLD = "269025201"

def getSettings():
	try:
		global settings
		configFile=open(os.environ['HOME']+"/.config/simple-power-manager/config.conf","r")
		#configFile=open("/home/kirbylife/.config/simple-power-manager/config.conf","r")
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
	except:
		configFile=open(os.environ['HOME']+"/.config/simple-power-manager/config.conf","w")
		for c in settings:
			configFile.write(c[0]+"="+str(c[1])+"\n")
		configFile.close()
		getSettings()

def resetTime(event=None):
	global inactiveTime
	inactiveTime=time.time()

def suspend(order,ssorder):
	if(ssorder=="1"):
		getoutput("xdg-screensaver lock")
	if(order=="1"):
		getoutput("systemctl suspend")
	elif(order=="2"):
		getoutput("systemctl hibernate")

def changeBright(value,dir):
	print ("entro")
	bus=dbus.SystemBus()
	kbdBacklightProxy = bus.get_object('org.freedesktop.UPower','/org/freedesktop/UPower/KbdBacklight')
	kbdBacklight = dbus.Interface(kbdBacklightProxy,'org.freedesktop.UPower.KbdBacklight')
	#max=int(kbdBacklight.GetMaxBrightness())
	#current=1
	max=100
	current=int(kbdBacklight.GetBrightness())
	if value:
		if(current<max):
			current=current+(5*max/100)%max
	else:
		if(current>0):
			current=current-(5*max/100)
			if(current<0):
				current=0
	#kbdBacklight.SetBrightness(current)

def kbevent(event):
	global running,settings,KBD,KBU,KSD,SLD
	resetTime()
	getSettings()
	key = str(event.Key)
	print (key)
	print (KBD)
	if KBD in key and settings[1][1]=="1":
		graphicCards=getoutput("ls /sys/class/backlight").split("\n")
		for c in graphicCards:
			changeBright(False,c)
	elif KBU in key and settings[1][1]=="1":
		graphicCards=getoutput("ls /sys/class/backlight").split("\n")
		for c in graphicCards:
			changeBright(True,c)
	elif KSD in key and settings[0][1]!="0":
		suspend(settings[0][1])
	elif SLD in key and settings[2][1]!="0":
		suspend(settings[2][1],settings[3][1])

def main(args):
	hookman = pyxhook.HookManager()
	hookman.KeyDown = kbevent
	hookman.KeyUp=hookman.MouseAllButtonsDown=hookman.MouseAllButtonsUp=hookman.MouseMovement=resetTime
	hookman.HookKeyboard()
	hookman.HookMouse()
	hookman.start()
	getSettings()
	while True:
		#(time.time()-inactiveTime)
		time.sleep(0.1)

	hookman.cancel()

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))

