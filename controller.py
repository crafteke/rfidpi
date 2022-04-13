import os
import time
import RPi.GPIO as GPIO
from signal import signal, SIGINT
from sys import exit
import socketio
import serial
import os

SIO_SERVER='http://face6core.local:4567'

sio = socketio.Client()
serials=[None]*6

correct_tags=["0415911acdc826","0415917a9b5728","0415910a76d926","0415910a66c326","0415918a11ac28","0415911a2ce826"]
GPIO.setmode(GPIO.BCM)
#
# @sio.event
# def connect():
#     print("Connected to server. Registering.")
#     sio.emit('Register','rfidpi')

@sio.event
def connect_error():
    print("The connection failed!")

@sio.event
def disconnect():
    print("Disconnected from server")

def main():
    print("Starting RFID serial watcher...")
    try:
       sio.connect(SIO_SERVER)
    except:
        print("SocketIO server not available")
    if sio.connected:
        sio.emit('Register',"rfidPi")
        print("Connected with SID ",sio.sid)
    print("Opening available serial ports... ")
    usb_devices_array=os.popen('ls /dev/ttyUSB*').read().split('\n')
    usb_devices_array=list(filter(lambda e: len(e)>0, usb_devices_array))
    i=0
    retries=0
    for ser_port in usb_devices_array:
        if(os.path.exists(ser_port)):
            serials[i]=serial.Serial()
            serials[i].baudrate = 115200
            serials[i].port = ser_port
            connected=False
            while not connected and retries<10:
                retries+=1
                try:
                    serials[i].open()
                    print("Port ",ser_port," opened.")
                    connected=True
                    i+=1
                except:
                    print("Error connecting ", ser_port," Retry...")
            retries=0
    while True:
        for i in range(0,6):
            if(serials[i]!= None and serials[i].in_waiting):
                data=serials[i].readline()
                data=data.decode("utf-8").strip()
                print("Received RFID:",data)
                msg={}
                rfid_id=data.split(':')[0]
                if(rfid_id in ["0","1","2","3","4","5"]): #ignore firmware dumping from arduino
                    msg["controller_id"]= "rfid_"+rfid_id
                    rfid=data.split(':')[1]
                    if(rfid=="TAG_GONE"):
                        msg["value"]=-1
                    elif rfid==correct_tags[i]:
                        msg["value"]=1
                    elif(rfid=="TAG_FOUND"):
                        msg["value"]=0
                    if sio.connected:
                        sio.emit('Command',msg)
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
