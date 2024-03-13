# module imports
from threading import *
import serial

# running the arduino in a seperate thread so that it doesn't interupt the app
class ArduinoThread():
    # init function, the function that will be run automatically
    def __init__(self, app):
        super().__init__()
        self.thread = Thread(target = self.work)
        # passing the mainwindow into this class so that we can change the text
        self.mainwindow = app
        # initializing reading values
        self.spo2 = 0
        self.fr = 0
        self.pulse = 0
    
    # starts the thread
    def start_thread(self):
        self.thread.start()

    # the function behind reading the arduinos
    def work(self):
            # begin instant serial monitor
            self.serial_inst = serial.Serial()
            self.serial_inst.baudrate=9600
            self.serial_inst.port="/dev/cu.usbmodem11402"
            self.serial_inst.open()
            self.serial_open = True

            # while serial monitor printing values
            while True:
                #use this to get data to read on terminal
                if self.serial_inst.in_waiting:
                    packet = self.serial_inst.readline()
                    line = packet.decode('utf').rstrip('\n')
                    
                    # seperate the readings into 3 seperate readings
                    readings = line.split(',')

                    self.spo2_list =[]


                    # assign the different values to their variable 
                    for item in readings:
                        letter, value = item.split(":")
                        if letter == "O":
                            self.spo2 = (float(value))
                        elif letter == "F":
                            self.fr = (int(value))
                        elif letter == "P":
                            self.pulse = (int(value))
                    
                    # change the values in the mainwindow
                    self.mainwindow.current_spo2(self.spo2)
                    self.mainwindow.spo2_label.configure(text=self.spo2)
                    self.mainwindow.fr_label.configure(text=self.fr)
                    self.mainwindow.pulse_label.configure(text=self.pulse)

    # fucntion to send a value back to the Arduino
    def write_to_arduino(self, value):
        # self.serial_inst.write(value.encode())
        pass