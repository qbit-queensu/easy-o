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
        self.mode_label = ctk.CTkLabel(self, text="MODE: AUTOMATIC", text_color="white")
        self.mode_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        # settings button - opens the settings screen when pushed
        self.setting_button = ctk.CTkButton(self, text="SETTINGS", text_color="white", fg_color="#878788", corner_radius=4, command=self.open_settings)
        self.setting_button.grid(row=0, column=4, padx=10, pady=10, sticky="ew")
        # spo2
        self.spo2_label = ctk.CTkLabel(self, text="Spo2:___", text_color="black", fg_color="#9eccf4", height=50, corner_radius=4)
        self.spo2_label.grid(row=2, column=0, padx=10, pady=20,  sticky="ew")
        # flow rate
        self.fr_label = ctk.CTkLabel(self, text="Flow Rate:___", text_color="black", fg_color="#9eccf4", height=50, corner_radius=4)
        self.fr_label.grid(row=3, column=0, padx=10, pady=20, sticky="ew")
        # pulse
        self.pulse_label = ctk.CTkLabel(self, text="Pulse:___", text_color="black", fg_color="#9eccf4", height=50, corner_radius=4)
        self.pulse_label.grid(row=4, column=0, padx=10, pady=20, sticky="ew")
        # spo2 graph
        self.spo2_graph = ctk.CTkLabel(self, text="Spo2 graph", text_color="black", fg_color="white", height=250, corner_radius=4)
        self.spo2_graph.grid(row=2, column=1, columnspan=4, rowspan=4, padx=10, pady=20, sticky="ew")

        # widgets fitted properly to the window
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)

        self.read_arduino()

    def read_arduino(self):   
        self.arduino_thread = ArduinoThread(self)
        self.arduino_thread.start_thread()

       # function to open the settings
    def open_settings(self):
        # creating the settings window as a pop up
        self.settings = ctk.CTkToplevel(self)
        # title and geomety of the settings screen
        self.settings.title("self.settings")
        w = 700
        h= 250
        self.settings.geometry('%dx%d+%d+%d' % (w, h, self.x, self.y))

        # creating the widgets for the pop up screen and displaying them using a grid
        # mode and discription - will change for each mode
        self.mode = ctk.CTkLabel(self.settings, text = "      MODE      ", text_color="white")
        self.mode.grid(column=0, row=0, padx=5, pady=5)
        self.description = ctk.CTkLabel(self.settings, text = "DESCRIPTION", text_color="white")
        self.description.grid(column=0, row=1, padx=5, pady=5)
        
        # spo2 inputs
        self.init_spo2_label = ctk.CTkLabel(self.settings, text = "    Init Spo2    ", text_color="black", fg_color="#9eccf4", corner_radius=4, width=20)
        self.init_spo2_label.grid(column=0, row=3, padx=2, pady=10)
        self.init_spo2_input = ctk.CTkEntry(self.settings, width=100)
        self.init_spo2_input.grid(column=1, row=3, padx=2, pady=10)
        
        self.min_spo2_label = ctk.CTkLabel(self.settings, text = "    Min Spo2    ", text_color="black", fg_color="#9eccf4", corner_radius=4)
        self.min_spo2_label.grid(column=0, row=4, padx=2, pady=10)
        self.min_spo2_input = ctk.CTkEntry(self.settings, width=100)
        self.min_spo2_input.grid(column=1, row=4, padx=2, pady=10)
        
        self.max_spo2_label = ctk.CTkLabel(self.settings, text = "    Max Spo2    ", text_color="black", fg_color="#9eccf4", corner_radius=4)
        self.max_spo2_label.grid(column=0, row=5, padx=2, pady=10)
        self.max_spo2_input = ctk.CTkEntry(self.settings, width=100)
        self.max_spo2_input.grid(column=1, row=5, padx=2, pady=10)
      
        # flow rate inputs
        self.init_flow_rate_label = ctk.CTkLabel(self.settings, text = "Init Flow Rate", text_color="black", fg_color="#9eccf4", corner_radius=4)
        self.init_flow_rate_label.grid(column=2, row=3, padx=2, pady=10)
        self.init_flow_rate_input = ctk.CTkEntry(self.settings, width=100)
        self.init_flow_rate_input.grid(column=3, row=3, padx=2, pady=10)
        
        self.min_flow_rate_label = ctk.CTkLabel(self.settings, text = "Min Flow Rate", text_color="black", fg_color="#9eccf4", corner_radius=4)
        self.min_flow_rate_label.grid(column=2, row=4, padx=2, pady=10)
        self.min_flow_rate_input = ctk.CTkEntry(self.settings, width=100)
        self.min_flow_rate_input.grid(column=3, row=4, padx=2, pady=10)
        
        self.max_flow_rate_label = ctk.CTkLabel(self.settings, text = "Max Flow Rate", text_color="black", fg_color="#9eccf4", corner_radius=4)
        self.max_flow_rate_label.grid(column=2, row=5, padx=2, pady=10)
        self.max_flow_rate_input = ctk.CTkEntry(self.settings, width=100)
        self.max_flow_rate_input.grid(column=3, row=5, padx=2, pady=10)
        
        # pulse inputs
        self.min_pulse_label = ctk.CTkLabel(self.settings, text = "    Min Pulse    ", text_color="black", fg_color="#9eccf4", corner_radius=4)
        self.min_pulse_label.grid(column=5, row=3, padx=2, pady=10)
        self.min_pulse_input = ctk.CTkEntry(self.settings, width=100)
        self.min_pulse_input.grid(column=6, row=3, padx=2, pady=10)
        
        self.max_pulse_label = ctk.CTkLabel(self.settings, text = "    Max Pulse    ", text_color="black", fg_color="#9eccf4", corner_radius=4)
        self.max_pulse_label.grid(column=5, row=4, padx=2, pady=10)
        self.max_pulse_input = ctk.CTkEntry(self.settings, width=100)
        self.max_pulse_input.grid(column=6, row=4, padx=2, pady=10)

        #switches mode
        self.mode_switch_button = ctk.CTkButton(self.settings, text="CHANGE MODE", text_color="white", fg_color="#878788", corner_radius=4)
        self.mode_switch_button.grid(row=0, column=6, padx=5, pady=5)

        # save button - sends the inputted values to the device and exits the self.settings screen
        self.save_button = ctk.CTkButton(self.settings, text = "SAVE", text_color="white", fg_color="#878788", corner_radius=4, command=self.close_settings)
        self.save_button.grid(column=5, row=5, columnspan=2)

        # widgets fitted properly to the window
        self.settings.grid_columnconfigure(0, weight=1)
        self.settings.grid_columnconfigure(1, weight=1)
        self.settings.grid_columnconfigure(2, weight=1)
        self.settings.grid_columnconfigure(3, weight=1)
    
    def close_settings(self):
        # saves the inputted values in a dictionary
        self.parameters = {}
        self.parameters['init_spo2_input'] = self.init_spo2_input.get().strip()
        self.parameters['min_spo2_input'] = self.min_spo2_input.get().strip()
        self.parameters['max_spo2_input'] = self.max_spo2_input.get().strip()
        self.parameters['init_flow_rate_input'] = self.init_flow_rate_input.get().strip()
        self.parameters['min_flow_rate_input'] = self.min_flow_rate_input.get().strip()
        self.parameters['max_flow_rate_input'] = self.max_flow_rate_input.get().strip()
        self.parameters['min_pulse_input'] = self.min_pulse_input.get().strip()
        self.parameters['max_pulse_input'] = self.max_pulse_input.get().strip()

        # check that all boxes have been filled
        for key, value in self.parameters.items():
            # if any of the boxes have not been filled, give an error
            if not value:
                CTkMessagebox(title="Error", message="Must add a value for each parameter", button_color="#9eccf4", button_text_color="black", cancel_button="None", icon="warning")
                return

        # close the settings window
        self.settings.destroy()
 
# run the app
if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()