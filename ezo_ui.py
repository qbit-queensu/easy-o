# import for custom tkinter
import customtkinter as ctk
from tkinter import *
from threading import *
import serial

# app theme
ctk.set_default_color_theme('dark-blue')
ctk.set_appearance_mode("dark")

class ArduinoThread():
    # init function, the function that will be run automatically
    def __init__(self, app):
        super().__init__()
        
        self.thread = Thread(target = self.work)

        self.mainwindow = app

        self.spo2 = 0
        self.fr = 0
        self.pulse = 0
    
    def start_thread(self):
        self.thread.start()

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
        settings = ctk.CTkToplevel(self)
        # title and geomety of the settings screen
        settings.title("Settings")
        w = 750
        h= 250
        settings.geometry('%dx%d+%d+%d' % (w, h, self.x, self.y))

        # creating the widgets for the pop up screen and displaying them using a grid
        # mode and discription - will change for each mode
        self.mode = ctk.CTkLabel(settings, text="AUTOMATIC", text_color="white")
        self.mode.grid(column=0, row=0, padx=5, pady=5)
        self.description = ctk.CTkLabel(settings, text = "automatic mode description", text_color="white")
        self.description.grid(column=0, row=1, padx=5, pady=5)
        # spo2 inputs
        init_spo2_label = ctk.CTkLabel(settings, text = "    Init Spo2    ", text_color="black", fg_color="#9eccf4", corner_radius=4, width=20)
        init_spo2_label.grid(column=0, row=3, padx=2, pady=10)
        init_spo2_input = ctk.CTkEntry(settings, width=100)
        init_spo2_input.grid(column=1, row=3, padx=2, pady=10)
        min_spo2_label = ctk.CTkLabel(settings, text = "    Min Spo2    ", text_color="black", fg_color="#9eccf4", corner_radius=4)
        min_spo2_label.grid(column=0, row=4, padx=2, pady=10)
        min_spo2_input = ctk.CTkEntry(settings, width=100)
        min_spo2_input.grid(column=1, row=4, padx=2, pady=10)
        max_spo2_label = ctk.CTkLabel(settings, text = "    Max Spo2    ", text_color="black", fg_color="#9eccf4", corner_radius=4)
        max_spo2_label.grid(column=0, row=5, padx=2, pady=10)
        max_spo2_input = ctk.CTkEntry(settings, width=100)
        max_spo2_input.grid(column=1, row=5, padx=2, pady=10)
        # flow rate inputs
        init_flow_rate_label = ctk.CTkLabel(settings, text = "Init Flow Rate", text_color="black", fg_color="#9eccf4", corner_radius=4)
        init_flow_rate_label.grid(column=2, row=3, padx=2, pady=10)
        init_flow_rate_input = ctk.CTkEntry(settings, width=100)
        init_flow_rate_input.grid(column=3, row=3, padx=2, pady=10)
        min_flow_rate_label = ctk.CTkLabel(settings, text = "Min Flow Rate", text_color="black", fg_color="#9eccf4", corner_radius=4)
        min_flow_rate_label.grid(column=2, row=4, padx=2, pady=10)
        min_flow_rate_input = ctk.CTkEntry(settings, width=100)
        min_flow_rate_input.grid(column=3, row=4, padx=2, pady=10)
        max_flow_rate_label = ctk.CTkLabel(settings, text = "Max Flow Rate", text_color="black", fg_color="#9eccf4", corner_radius=4)
        max_flow_rate_label.grid(column=2, row=5, padx=2, pady=10)
        max_flow_rate_input = ctk.CTkEntry(settings, width=100)
        max_flow_rate_input.grid(column=3, row=5, padx=2, pady=10)
        # pulse inputs
        min_pulse_label = ctk.CTkLabel(settings, text = "    Min Pulse    ", text_color="black", fg_color="#9eccf4", corner_radius=4)
        min_pulse_label.grid(column=5, row=3, padx=2, pady=10)
        min_pulse_input = ctk.CTkEntry(settings, width=100)
        min_pulse_input.grid(column=6, row=3, padx=2, pady=10)
        max_pulse_label = ctk.CTkLabel(settings, text = "    Max Pulse    ", text_color="black", fg_color="#9eccf4", corner_radius=4)
        max_pulse_label.grid(column=5, row=4, padx=2, pady=10)
        max_pulse_input = ctk.CTkEntry(settings, width=100)
        max_pulse_input.grid(column=6, row=4, padx=2, pady=10)
        # save button - sends the inputted values to the device and exits the settings screen
        save_button = ctk.CTkButton(settings, text = "SAVE", text_color="white", fg_color="#878788", corner_radius=4, command=settings.destroy)
        save_button.grid(column=5, row=5, columnspan=2)
        #switches mode
        mode_switch_button = ctk.CTkButton(settings, text="CHANGE MODE", text_color="white", fg_color="#878788", corner_radius=4, command=self.change_mode)
        mode_switch_button.grid(row=0, column=6, padx=5, pady=5)

        # widgets fitted properly to the window
        settings.grid_columnconfigure(0, weight=1)
        settings.grid_columnconfigure(1, weight=1)
        settings.grid_columnconfigure(2, weight=1)
        settings.grid_columnconfigure(3, weight=1)

    def change_mode(self):
        current_mode = self.mode_label.cget("text")
        if current_mode == "MODE: AUTOMATIC":
            new_mode = "MODE: MANUAL"
            self.description.configure(text = "manual mode description")
        elif current_mode == "MODE: MANUAL":
            new_mode = "MODE: AUTOMATIC"
            self.description.configure(text = "automatic mode description")
        self.mode_label.configure(text=new_mode)
        self.mode.configure(text = new_mode)

        
        
# run the app
if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()