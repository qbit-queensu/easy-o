from threading import Thread
import serial
import statistics

# reads the arduino and 
class ArduinoThread():
    def __init__(self, app):
        super().__init__()
        self.thread = Thread(target=self.work)
        self.mainwindow = app
        self.spo2_readings = []
        self.fr_readings = []
        self.pulse_readings = []
        self.num_readings_to_average = 10

    def start_thread(self):
        self.thread.start()

    def work(self):
        self.serial_inst = serial.Serial()
        self.serial_inst.baudrate = 9600
        self.serial_inst.port = "/dev/cu.usbmodem11402"
        self.serial_inst.open()
        self.serial_open = True

        while True:
            if self.serial_inst.in_waiting:
                packet = self.serial_inst.readline()
                line = packet.decode('utf').rstrip('\n')
                
                readings = line.split(',')

                for item in readings:
                    letter, value = item.split(":")
                    value = float(value)
                    if letter == "O":
                        self.spo2_readings.append(value)
                    elif letter == "F":
                        self.fr_readings.append(value)
                    elif letter == "P":
                        self.pulse_readings.append(value)

                if len(self.spo2_readings) >= self.num_readings_to_average:
                    spo2_avg = self.calculate_filtered_average(self.spo2_readings)
                    self.mainwindow.current_spo2(spo2_avg)
                    self.mainwindow.spo2_label.configure(text=f'Spo2: {spo2_avg:.2f}')
                    self.spo2_readings = []

                if len(self.fr_readings) >= self.num_readings_to_average:
                    fr_avg = self.calculate_filtered_average(self.fr_readings)
                    self.mainwindow.current_flowrate(fr_avg)
                    self.mainwindow.fr_label.configure(text=f'Flowrate: {fr_avg:.2f}')
                    self.fr_readings = []

                if len(self.pulse_readings) >= self.num_readings_to_average:
                    pulse_avg = self.calculate_filtered_average(self.pulse_readings)
                    self.mainwindow.pulse_label.configure(text=f'Pulse: {pulse_avg:.2f}')
                    self.pulse_readings = []

    def calculate_filtered_average(self, readings):
        # Filter out outliers using a simple approach like removing values beyond 2 standard deviations
        filtered_readings = [x for x in readings if abs(x - statistics.mean(readings)) < 2] # line not working properly
        
        # Calculate the average of filtered readings
        return round(statistics.mean(readings), 3)


    def write_to_arduino(self, value):
        intro = "valve_open: "
        valve_value_to_send = str(value)
        send = intro + valve_value_to_send
        self.serial_inst.write(valve_value_to_send.encode())
