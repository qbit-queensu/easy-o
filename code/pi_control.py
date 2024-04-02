# module imports
from threading import *
import time

# PI control for the % valve open
class AutoPIController():
    def __init__(self, main_window, Kp, Ki, sampling_time, target_spo2):
        self.thread = Thread(target = self.work)
        # initializing parameters
        self.main_window = main_window
        self.Kp = Kp
        self.Ki = Ki
        self.sampling_time = sampling_time
        self.target_spo2 = target_spo2
        self.integral_sum = 0

    # starts the thread
    def start_thread(self):
        self.thread.start()

    # update the % valve open
    def work(self):
        while True:
            valve_open = self.main_window.valve_open
            real_spo2 = self.main_window.current_spo2_value
            e_prev = 0
            I = 0

            # algorithm for determining % valve open
            e = self.target_spo2 - real_spo2
            P = self.Kp*e
            I = I + self.Ki*e*(self.sampling_time)

            valve_open = valve_open + P + I

            # send the updated % valve open back to the main_window
            self.main_window.valve_open_to_arduino(valve_open)
            self.main_window.update_control_plot(real_spo2, valve_open)
            
            # wait until it is new interval for calculation
            time.sleep(self.sampling_time)


# PI control for the % valve open
class ManualPIController():
    def __init__(self, main_window, Kp, Ki, sampling_time, target_flowrate):
        self.thread = Thread(target = self.work)
        # initializing parameters
        self.main_window = main_window
        self.Kp = Kp
        self.Ki = Ki
        self.sampling_time = sampling_time
        self.target_flowrate = target_flowrate
        self.integral_sum = 0

    # starts the thread
    def start_thread(self):
        self.thread.start()

    # update the % valve open
    def work(self):
        while True:
            valve_open = self.main_window.valve_open
            real_flowrate = self.main_window.current_flowrate_value
            e_prev = 0
            I = 0

            # algorithm for determining % valve open
            e = self.target_flowrate - real_flowrate
            P = self.Kp*e
            I = I + self.Ki*e*(self.sampling_time)

            valve_open = valve_open + P + I

            # send the updated % valve open back to the main_window
            self.main_window.valve_open_to_arduino(valve_open)
            
            # wait until it is new interval for calculation
            time.sleep(self.sampling_time)