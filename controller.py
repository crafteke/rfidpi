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
VALIDATE_BUTTON=4
START_BUILDING=17
#
# @sio.event
# def connect():
#     print("Connected to server. Registering.")
#     sio.emit('Register','rfidpi')

def push_validate(channel):
    msg={}
    print("Validation button pushed.")
    for i in range(0,6):
        if(serials[i]!= None):
            serials[i].write(bytes('1', 'utf-8'))
    msg["controller_id"]="rfid_button_validate"
    msg['value']=1
    if sio.connected:
        sio.emit('Command',msg)

def push_build(channel):
    msg={}
    print("Launch button pushed.")
    msg["controller_id"]="rfid_button_launch"
    msg['value']=1
    if sio.connected:
        sio.emit('Command',msg)

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

    GPIO.setup(VALIDATE_BUTTON, GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(START_BUILDING,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(VALIDATE_BUTTON, GPIO.FALLING, callback=push_validate, bouncetime=300)
    GPIO.add_event_detect(START_BUILDING, GPIO.FALLING, callback=push_build,bouncetime=300)
    while True:
        for i in range(0,6):
            if(serials[i]!= None and serials[i].in_waiting):
                data=serials[i].readline()
                data=data.decode("utf-8").strip()
                print("Received RFID:",data)
                msg={}
                serial_msg=data.split(':')
                rfid_id=serial_msg[0]
                if(rfid_id in ["0","1","2","3","4","5"]): #ignore firmware dumping from arduino
                    msg["controller_id"]= "rfid_"+rfid_id
                    rfid=serial_msg[1]
                    if(rfid=="TAG_GONE"):
                        msg["value"]=0
                    elif rfid==correct_tags[i]:
                        if(len(serial_msg)==3 and serial_msg[2]=='R'):
                            msg["value"]=2
                        else:
                            msg["value"]=1
                    else:
                        if(len(serial_msg)==3 and serial_msg[2]=='R'):
                            msg["value"]=-2
                        else:
                            msg["value"]=-1
                    if sio.connected:
                        sio.emit('Command',msg)
        time.sleep(0.1)

def requestRefresh():
    serials.write(1)
def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    sio.disconnect()
    for ser in serials:
        if(ser != None):
            ser.close()
    #GPIO.cleanup()

    exit(0)
@sio.event
def Command(data):
    if(data['controller_id']=='rfid_button_calibrate' and data['value']=='1'):
        print("Calibration of rfid.")
        for i in range(0,6):
            if(serials[i]!= None):
                serials[i].write(bytes('2', 'utf-8'))

if __name__ == "__main__":
    signal(SIGINT, handler)
    main()
