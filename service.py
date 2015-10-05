import urllib2
import threading
import xbmcgui
import calendar
import time
import sys

from HTMLParser import HTMLParser
from os import system
from apscheduler.scheduler import Scheduler


class OasthParser(HTMLParser):

  def __init__(self):
    HTMLParser.__init__(self)
    self.recording = 0
    self.data = []

  def handle_starttag(self, tag, attrs):
    if tag == 'div':
      for name, value in attrs:
        if value=='menu':
          self.recording =1

  def handle_endtag(self, tag):
    if tag == 'div' and self.recording!=0:
      self.recording -=1
  def handle_data(self, data):
    if self.recording>0:
      self.data.append(data)

def findBuses():
  p = OasthParser()
  busLines=[]
  f = urllib2.urlopen('http://m.oasth.gr/index.php?md=3&sn=3&start=4483&sorder=1&rc=973&line=434&dir=1')
  html = f.read()
  p.feed(html)

  numberOfBuses= len(p.data)/3
  id=p.data[0::3]
  time= p.data[2::3]

  if numberOfBuses>0:
    for x in  range(0, numberOfBuses):
      busLines.append("Bus Number: {0} Arriving in: {1} ".format( id[x],time[x]))
  else:
    busLines.append("There are no buses right now.")


  p.close()
  return busLines

class OasthWindow(xbmcgui.WindowDialog):
  def __init__(self):
    winWidth=self.getWidth()
    self.addControl(xbmcgui.ControlImage(x=0, y=0, width=1920, height=1080, filename='/storage/.xbmc/addons/service.oasth/back.jpg'))
    self.addControl(xbmcgui.ControlLabel(x=winWidth/2-100 , y=25, width= 200 , height=250, label="Bus Arrivals", font="Font30"))
    self.exitButton=xbmcgui.ControlButton(x=winWidth/2-50 ,y=350,width=100,height=50,label="Close",font="Font30")
    self.addControl(self.exitButton)
    self.setFocus(self.exitButton)

  def onControl(self, control):
    if control ==self.exitButton:
     system("reboot")


def showBuses(window):
  winWidth=window.getWidth()
  busInfo=findBuses()
  busList=[]
  print busInfo[0]
  posY=70
  for x in range(0,len(busInfo)):
    bus=xbmcgui.ControlLabel(x=winWidth/2-250 , y=posY, width= 500 , height=250, label=busInfo[x], font="font16")
    window.addControl(bus)
    busList.append(bus)
    posY+=50

  xbmc.sleep(10000)
  for x in range(0,len(busInfo)):
    window.removeControl(busList[x])


def powerTV():
  system("echo 'as 1'| cec-client -s")

def runMod():
  powerTV()
  timeStart=calendar.timegm(time.gmtime())
  timeStop = timeStart+3600
  window = OasthWindow()
  window.show()
  while calendar.timegm(time.gmtime())<timeStop and window:
    showBuses(window)
  if(window):
    window.close()

if __name__ == "__main__":
  sched = Scheduler(standalone=True)
  sched.add_cron_job(runMod,day_of_week='mon-fri', hour=9)
  sched.start()

