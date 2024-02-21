# import for custom tkinter
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from tkinter import *
from threading import *
import serial

# app theme
ctk.set_default_color_theme('dark-blue')
ctk.set_appearance_mode("dark")

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
            serialInst = serial.Serial()
            serialInst.baudrate=9600
            serialInst.port="/dev/cu.usbmodem1202"
            serialInst.open()

            # while serial monitor printing values
            while True:
                #use this to get data to read on terminal
                if serialInst.in_waiting:
                    packet=serialInst.readline()
                    line = packet.decode('utf').rstrip('\n')
                    
                    # seperate the readings into 3 seperate readings
                    readings = line.split(',')

                    # assign the different values to their variable 
                    for item in readings:
                        letter, value = item.split(":")
                        if letter == "O":
                            self.spo2 = (int(value))
                        elif letter == "F":
                            self.fr = (int(value))
                        elif letter == "P":
                            self.pulse = (int(value))
                    
                    # change the text in the mainwindow
                    self.mainwindow.spo2_label.configure(text=self.spo2)
                    self.mainwindow.fr_label.configure(text=self.fr)
                    self.mainwindow.pulse_label.configure(text=self.pulse)

                    # printing the readings
                    print("Spo2:", self.spo2)
                    print("Flowrate:", self.fr)
                    print("Pulse:", self.pulse)


# main window of the UI
class MainWindow(ctk.CTk):
# init function, the function that will be run automatically
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # title and geometry of the main wndow
        self.title("Easy-O UI")      
        # place the window in the middle of the screen
        w = 750
        h = 330
        # get screen width and height
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        # calculate x and y coordinates for the window to open in
        self.x = (ws/2) - (w/2)
        self.y = (hs/2) - (h/2)
        self.geometry('%dx%d+%d+%d' % (w, h, self.x, self.y))

        # creating all the widgets for the main window and displaying them using a grid
        # mode - will change between AUTOMATIC and MANUAL
        self.mode_label = ctk.CTkLabel(self, text="Automatic Mode", text_color="white")
        self.mode_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.mode_button = ctk.CTkButton(self, text="Change Mode", text_color="white", fg_color="#878788", corner_radius=4, command=self.change_mode)
        self.mode_button.grid(row=1, column=0, padx=10, sticky="ew")
        # settings button - opens the settings screen when pushed
        self.setting_button = ctk.CTkButton(self, text="SETTINGS", text_color="white", fg_color="#878788", corner_radius=4, command=self.open_settings)
        self.setting_button.grid(row=0, column=4, padx=10, pady=5, sticky="ew")
        # spo2
        self.spo2_label = ctk.CTkLabel(self, text="Spo2:___", text_color="black", fg_color="#9eccf4", height=50, corner_radius=4)
        self.spo2_label.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        # flow rate
        self.fr_label = ctk.CTkLabel(self, text="Flow Rate:___", text_color="black", fg_color="#9eccf4", height=50, corner_radius=4)
        self.fr_label.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        # pulse
        self.pulse_label = ctk.CTkLabel(self, text="Pulse:___", text_color="black", fg_color="#9eccf4", height=50, corner_radius=4)
        self.pulse_label.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        # spo2 graph
        self.spo2_graph = ctk.CTkLabel(self, text="Spo2 graph", text_color="black", fg_color="white", height=250, corner_radius=4)
        self.spo2_graph.grid(row=2, column=1, columnspan=4, rowspan=4, padx=10, pady=20, sticky="ew")

        # widgets fitted properly to the window
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)

        self.read_arduino()
        self.auto_settings = None
        self.manual_settings = None
        
        self.mode = "auto"

    # start the arduino thread
    def read_arduino(self):   
        self.arduino_thread = ArduinoThread(self)
        self.arduino_thread.start_thread()

    # change mode
    def change_mode(self):
        if self.mode == "auto":
            self.mode = "manual"
            self.mode_label.configure(text="Manual Mode")
        elif self.mode == "manual":
            self.mode = "auto"
            self.mode_label.configure(text="Automatic Mode")
    
    # open settings screen based on chosen mode
    def open_settings(self):
        if self.mode == "auto":
            self.open_auto_settings()
        elif self.mode == "manual":
            self.open_manual_settings()
   
    # automatic settings screen
    def open_auto_settings(self):
        if self.auto_settings is None:
            # creating the settings window as a pop up
            self.auto_settings = ctk.CTkToplevel(self)
            # title and geomety of the settings screen
            self.auto_settings.title("Automatic Settings")
            w = 750
            h= 330
            self.auto_settings.geometry('%dx%d+%d+%d' % (w, h, self.x, self.y))

            # creating the widgets for the pop up screen and displaying them using a grid
            # mode and discription - will change for each mode
            self.mode = ctk.CTkLabel(self.auto_settings, text = "    Automatic    ", text_color="white")
            self.mode.grid(column=0, row=0, padx=5, pady=5, sticky="ew")
            self.description = ctk.CTkLabel(self.auto_settings, text = "DESCRIPTION", text_color="white")
            self.description.grid(column=0, row=1, padx=5, pady=10, sticky="ew")
            
            # spo2 inputs
            self.init_spo2_label = ctk.CTkLabel(self.auto_settings, text = "    Init Spo2    ", text_color="black", fg_color="#9eccf4", corner_radius=4, width=20)
            self.init_spo2_label.grid(column=0, row=3, padx=4, pady=10, sticky="ew")
            self.init_spo2_input = ctk.CTkEntry(self.auto_settings, width=100)
            self.init_spo2_input.grid(column=1, row=3, padx=4, pady=10, sticky="ew")
            
            self.min_spo2_label = ctk.CTkLabel(self.auto_settings, text = "    Min Spo2    ", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.min_spo2_label.grid(column=0, row=4, padx=4, pady=10, sticky="ew")
            self.min_spo2_input = ctk.CTkEntry(self.auto_settings, width=100)
            self.min_spo2_input.grid(column=1, row=4, padx=4, pady=10, sticky="ew")
            
            self.max_spo2_label = ctk.CTkLabel(self.auto_settings, text = "    Max Spo2    ", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.max_spo2_label.grid(column=0, row=5, padx=4, pady=10, sticky="ew")
            self.max_spo2_input = ctk.CTkEntry(self.auto_settings, width=100)
            self.max_spo2_input.grid(column=1, row=5, padx=4, pady=10, sticky="ew")
        
            # flow rate inputs
            self.init_flow_rate_label = ctk.CTkLabel(self.auto_settings, text = "Init Flow Rate", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.init_flow_rate_label.grid(column=2, row=3, padx=4, pady=10, sticky="ew")
            self.init_flow_rate_input = ctk.CTkEntry(self.auto_settings, width=100)
            self.init_flow_rate_input.grid(column=3, row=3, padx=4, pady=10, sticky="ew")
            
            self.min_flow_rate_label = ctk.CTkLabel(self.auto_settings, text = "Min Flow Rate", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.min_flow_rate_label.grid(column=2, row=4, padx=4, pady=10, sticky="ew")
            self.min_flow_rate_input = ctk.CTkEntry(self.auto_settings, width=100)
            self.min_flow_rate_input.grid(column=3, row=4, padx=4, pady=10, sticky="ew")
            
            self.max_flow_rate_label = ctk.CTkLabel(self.auto_settings, text = "Max Flow Rate", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.max_flow_rate_label.grid(column=2, row=5, padx=4, pady=10, sticky="ew")
            self.max_flow_rate_input = ctk.CTkEntry(self.auto_settings,  width=100)
            self.max_flow_rate_input.grid(column=3, row=5, padx=4, pady=10, sticky="ew")
            
            # pulse inputs
            self.min_pulse_label = ctk.CTkLabel(self.auto_settings, text = "    Min Pulse    ", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.min_pulse_label.grid(column=5, row=3, padx=4, pady=10, sticky="ew")
            self.min_pulse_input = ctk.CTkEntry(self.auto_settings, width=100)
            self.min_pulse_input.grid(column=6, row=3, padx=4, pady=10, sticky="ew")
            
            self.max_pulse_label = ctk.CTkLabel(self.auto_settings, text = "    Max Pulse    ", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.max_pulse_label.grid(column=5, row=4, padx=4, pady=10, sticky="ew")
            self.max_pulse_input = ctk.CTkEntry(self.auto_settings, width=100)
            self.max_pulse_input.grid(column=6, row=4, padx=4, pady=10, sticky="ew")

            # time interval for evaluaiton
            self.interval_label = ctk.CTkLabel(self.auto_settings, text = "       Interval      ", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.interval_label.grid(column=5, row=5, padx=4, pady=10, sticky="ew")
            self.interval_input = ctk.CTkEntry(self.auto_settings, width=100)
            self.interval_input.grid(column=6, row=5, padx=4, pady=10, sticky="ew")

            # save button - sends the inputted values to the device and exits the self.auto_settings screen
            self.save_button = ctk.CTkButton(self.auto_settings, text = "SAVE", text_color="white", fg_color="#878788", corner_radius=4, command=self.save_auto_variables)
            self.save_button.grid(column=6, row=6, columnspan=1, padx=4, pady=10, sticky="ew")

            # text box for error messages
            self.error_message = ctk.CTkLabel(self.auto_settings, text="", text_color="white")
            self.error_message.grid(column=1, row=6, columnspan=4, pady=2)

            # widgets fitted properly to the window
            self.auto_settings.grid_columnconfigure(0, weight=1)
            self.auto_settings.grid_columnconfigure(1, weight=1)
            self.auto_settings.grid_columnconfigure(2, weight=1)
            self.auto_settings.grid_columnconfigure(3, weight=1)

        else:
            self.auto_settings.deiconify()
   
    def save_auto_variables(self):
        # saves the inputted values in a dictionary
        parameters_full = False
        self.parameters = {}
        self.parameters['init_spo2_input'] = self.init_spo2_input.get()
        self.parameters['min_spo2_input'] = self.min_spo2_input.get()
        self.parameters['max_spo2_input'] = self.max_spo2_input.get()
        self.parameters['init_flow_rate_input'] = self.init_flow_rate_input.get()
        self.parameters['min_flow_rate_input'] = self.min_flow_rate_input.get()
        self.parameters['max_flow_rate_input'] = self.max_flow_rate_input.get()
        self.parameters['min_pulse_input'] = self.min_pulse_input.get()
        self.parameters['max_pulse_input'] = self.max_pulse_input.get()
        self.parameters['interval_input'] = self.interval_input.get()

        # check that all boxes have been filled
        if '' in self.parameters.values():
            self.error_message.configure(text="Must enter a value for each parameter!")
        else:
            parameters_full = True
    
        # if there is input for each value, close settings window
        if parameters_full:
            self.close_settings(self.auto_settings)

    # manual settings screen
    def open_manual_settings(self):
        if self.manual_settings is None:
            # creating the settings window as a pop up
            self.manual_settings = ctk.CTkToplevel(self)
            # title and geomety of the settings screen
            self.manual_settings.title("Manual Settings")
            w = 750
            h= 330
            self.manual_settings.geometry('%dx%d+%d+%d' % (w, h, self.x, self.y))

            # creating the widgets for the pop up screen and displaying them using a grid
            # mode and discription - will change for each mode
            self.m_mode = ctk.CTkLabel(self.manual_settings, text = "     MANUAL     ", text_color="white")
            self.m_mode.grid(column=0, row=0, padx=5, pady=10, sticky="ew")
            self.m_description = ctk.CTkLabel(self.manual_settings, text = "DESCRIPTION", text_color="white")
            self.m_description.grid(column=0, row=1, padx=5, pady=10, sticky="ew")
            
            # spo2 inputs
            self.m_min_spo2_label = ctk.CTkLabel(self.manual_settings, text = "  Min Spo2  ", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.m_min_spo2_label.grid(column=0, row=3, padx=4, pady=10, sticky="ew")
            self.m_min_spo2_input = ctk.CTkEntry(self.manual_settings, width=100)
            self.m_min_spo2_input.grid(column=1, row=3, padx=4, pady=10, sticky="ew")
            
            self.m_max_spo2_label = ctk.CTkLabel(self.manual_settings, text = "  Max Spo2  ", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.m_max_spo2_label.grid(column=0, row=4, padx=4, pady=10, sticky="ew")
            self.m_max_spo2_input = ctk.CTkEntry(self.manual_settings, width=100)
            self.m_max_spo2_input.grid(column=1, row=4, padx=4, pady=10, sticky="ew")
        
            # flow rate inputs
            self.m_set_flow_rate_label = ctk.CTkLabel(self.manual_settings, text = "  Flow Rate  ", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.m_set_flow_rate_label.grid(column=2, row=3, padx=4, pady=10, sticky="ew")
            self.m_set_flow_rate_input = ctk.CTkEntry(self.manual_settings, width=100)
            self.m_set_flow_rate_input.grid(column=3, row=3, padx=4, pady=10, sticky="ew")
            
            # pulse inputs
            self.m_min_pulse_label = ctk.CTkLabel(self.manual_settings, text = "    Min Pulse    ", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.m_min_pulse_label.grid(column=5, row=3, padx=4, pady=10, sticky="ew")
            self.m_min_pulse_input = ctk.CTkEntry(self.manual_settings, width=100)
            self.m_min_pulse_input.grid(column=6, row=3, padx=4, pady=10, sticky="ew")
            
            self.m_max_pulse_label = ctk.CTkLabel(self.manual_settings, text = "    Max Pulse    ", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.m_max_pulse_label.grid(column=5, row=4, padx=4, pady=10, sticky="ew")
            self.m_max_pulse_input = ctk.CTkEntry(self.manual_settings, width=100)
            self.m_max_pulse_input.grid(column=6, row=4, padx=4, pady=10, sticky="ew")

            # save button - sends the inputted values to the device and exits the self.manual_settings screen
            self.save_button = ctk.CTkButton(self.manual_settings, text = "SAVE", text_color="white", fg_color="#878788", corner_radius=4, command=self.save_manual_variables)
            self.save_button.grid(column=5, row=6, columnspan=2, pady=10, sticky="ew")

            # text box for error messages
            self.error_message = ctk.CTkLabel(self.manual_settings, text="", text_color="white")
            self.error_message.grid(column=1, row=6, columnspan=4, pady=10, sticky="ew")

            # widgets fitted properly to the window
            self.manual_settings.grid_columnconfigure(0, weight=1)
            self.manual_settings.grid_columnconfigure(1, weight=1)
            self.manual_settings.grid_columnconfigure(2, weight=1)
            self.manual_settings.grid_columnconfigure(3, weight=1)

        else:
            self.manual_settings.deiconify()

    def save_manual_variables(self):
        # saves the inputted values in a dictionary
        parameters_full = False
        self.m_parameters = {}
        self.m_parameters['m_min_spo2_input'] = self.m_min_spo2_input.get()
        self.m_parameters['m_max_spo2_input'] = self.m_max_spo2_input.get()
        self.m_parameters['m_set_flow_rate_input'] = self.m_set_flow_rate_input.get()
        self.m_parameters['m_min_pulse_input'] = self.m_min_pulse_input.get()
        self.m_parameters['m_max_pulse_input'] = self.m_max_pulse_input.get()

        # check that all boxes have been filled
        if '' in self.m_parameters.values():
            self.error_message.configure(text="Must enter a value for each parameter!")
        else:
            parameters_full = True
            self.error_message.configure(text="")
    
        # if there is input for each value, close settings window
        if parameters_full:
            self.close_settings(self.manual_settings)

    # function to close the settings screen
    def close_settings(self, settings):
        # close the settings window
        settings.withdraw()
 
# run the app
if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()