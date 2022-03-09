import os
import time
import RPi.GPIO as GPIO
from signal import signal, SIGINT
from sys import exit
import socketio
import serial
import os

sio = socketio.Client()
serials=[None]*6

GPIO.setmode(GPIO.BCM)

@sio.event
def connect():
    print("Connected to server. Registering.")
    sio.emit('Register','cubeFaces')

@sio.event
def connect_error():
    print("The connection failed!")

@sio.event
def disconnect():
    print("Disconnected from server")

def main():
    print("Starting RFID serial watcher...")
    #sio.connect('http://crftk42.local:4567')
    sio.connect('http://crftk42.local:4567')
    print("Connected with SID ",sio.sid)
    print("Opening available serial ports... ")
    usb_devices_array=os.popen('ls /dev/ttyUSB*').read().split('\n')
    usb_devices_array=list(filter(lambda e: len(e)>0, usb_devices_array))
    i=0
    for ser_port in usb_devices_array:
        if(os.path.exists(ser_port)):
            serials[i]=serial.Serial()
            serials[i].baudrate = 115200
            serials[i].port = ser_port
            connected=False
            while not connected:
                try:
                    serials[i].open()
                    print("Port ",ser_port," opened.")
                    connected=True
                    i+=1
                except:
                    print("Error connecting ", ser_port," Retry...")
    while True:
        for i in range(0,6):
            if(serials[i]!= None and serials[i].in_waiting):
                data=serials[i].readline()
                data=data.decode("utf-8").strip()
                print("Received:",data)
                msg={}
                msg["data"]= data
                sio.emit('Event',msg)
        time.sleep(0.1)


def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    sio.disconnect()
    for ser in serials:
        if(ser != None):
            ser.close()
    #GPIO.cleanup()
    exit(0)

if __name__ == "__main__":
    signal(SIGINT, handler)
    main()
