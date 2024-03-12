# import for custom tkinter
import customtkinter as ctk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from threading import *
import serial
import time

# app theme
ctk.set_default_color_theme('dark-blue')
ctk.set_appearance_mode("dark")

# keypad to open when input box pressed
class CustomKeypad:
    def __init__(self, main_window, entry):
        self.main_window = main_window
        self.entry = entry
        self.keypad_frame = None
        self.display_var = tk.StringVar()
        self.display_var.set('')

    # create the keypad for particular entry box
    def create_keypad(self):
        self.update_display()
        # make a keypad
        self.keypad_frame = ctk.CTkToplevel(self.main_window)
        self.keypad_frame.title("Keypad")
        self.keypad_frame.protocol("WM_DELETE_WINDOW", self.close_keypad)

        # display
        display = ctk.CTkLabel(self.keypad_frame, textvariable=self.display_var, width=10)
        display.grid(row=0, column=0, columnspan=3)

        # place the keypad in the middle of the screen
        self.w = 450
        self.h = 180
        # get screen width and height
        self.ws = self.main_window.ws
        self.hs = self.main_window.hs
        # calculate x and y coordinates for the window to open in
        self.x = (self.ws/2) - (self.w/2)
        self.y = (self.hs/2) - (self.h/2)
        self.keypad_frame.geometry('%dx%d+%d+%d' % (self.w, self.h, self.x, self.y))

        # define buttons
        buttons = [
            '1', '2', '3',
            '4', '5', '6',
            '7', '8', '9',
            '0', 'Clear', 'Enter'
        ]

        # dreate buttons
        row = 1
        col = 0
        for button_text in buttons:
            button = ctk.CTkButton(self.keypad_frame, text=button_text, command=lambda text=button_text: self.on_button_click(text), text_color="white", fg_color="#878788", corner_radius=4)
            button.grid(row=row, column=col, padx=5, pady=5)
            col += 1
            if col > 2:
                col = 0
                row += 1

    # update the number display on the keypad
    def update_display(self):
        current_text = self.entry.get()
        self.display_var.set(current_text)

    # connect buttons to function
    def on_button_click(self, text):
        if text == 'Clear':
            self.entry.delete(0, tk.END)
            self.update_display()
        elif text == 'Enter':
            self.close_keypad()
        else:
            current_text = self.entry.get()
            new_text = current_text + text
            self.entry.delete(0, tk.END)
            self.entry.insert(0, new_text)
            self.update_display()

    # hide keypad
    def close_keypad(self):
        if self.keypad_frame:
            self.keypad_frame.destroy()


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

# PI control for the % valve open
class PIController():
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
            # 
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


# main window of the UI
class MainWindow(ctk.CTk):
# init function, the function that will be run automatically
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # title and geometry of the main wndow
        self.title("Easy-O UI")      
        # place the window in the middle of the screen
        self.w = 750
        self.h = 330
        # get screen width and height
        self.ws = self.winfo_screenwidth()
        self.hs = self.winfo_screenheight()
        # calculate x and y coordinates for the window to open in
        self.x = (self.ws/2) - (self.w/2)
        self.y = (self.hs/2) - (self.h/2)
        self.geometry('%dx%d+%d+%d' % (self.w, self.h, self.x, self.y))

        # creating all the widgets for the main window and displaying them using a grid
        # mode - will change between AUTOMATIC and MANUAL
        self.main_mode_label = ctk.CTkLabel(self, text="Automatic Mode", text_color="white")
        self.main_mode_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.main_mode_button = ctk.CTkButton(self, text="Change Mode", text_color="white", fg_color="#878788", corner_radius=4, command=self.change_mode)
        self.main_mode_button.grid(row=1, column=0, padx=10, sticky="ew")
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
        self.fig, self.ax = plt.subplots(figsize=(1, 1))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=1, column=1, columnspan=4, rowspan=4, padx=10, pady=20, sticky="ew")
        # initialize the line object for the plot
        self.live_spo2_list = []
        self.line, = self.ax.plot([], [], "#9eccf4")
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Spo2')
        self.ax.set_xlim(0, 1000)
        self.ax.set_ylim(-1, 1)

        # widgets fitted properly to the window
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)

        # set Nones
        self.auto_settings = None
        self.control_plots = None
        self.manual_settings = None
        self.pi_controller = None

        # initialize control lists
        self.control_live_valve_list = []
        self.control_live_spo2_list = []
        
        # set initial mode
        self.mode = "auto"

        # configure dictionary with keypads
        self.keypads = {}

        # configuring arduino
        self.arduino_communication()

    # calculate % that valve needs to be open based on flow rate
    def valve_open_calculation(self, flowrate):
        calculated_valve_open_percent = ((15 - flowrate)/ 15)*100
        self.valve_open_to_arduino(calculated_valve_open_percent)

    # send valve open percent to the arduino
    def valve_open_to_arduino(self, valve_percent_open):
        self.valve_open = valve_percent_open
        self.arduino_thread.write_to_arduino(self.valve_open)

    # save the current spo2 readings
    def current_spo2(self, spo2_value):
        self.current_spo2_value = float(spo2_value)
        self.update_plot(self.current_spo2_value)
    
    # value to update live plot
    def update_plot(self, spo2):
        if len(self.live_spo2_list) < 1000:
            self.live_spo2_list.append(spo2)
        else:
            self.live_spo2_list = []
            self.live_spo2_list.append(spo2)
        
        # update the plot data
        self.line.set_xdata(range(len(self.live_spo2_list)))
        self.line.set_ydata(self.live_spo2_list)

        # redraw the canvas
        self.canvas.draw()
    
    # bind entry box to a keypad
    def bind_entry_to_keypad(self, entry):
        entry.bind("<Button-1>", lambda event, entry=entry: self.open_keypad(event, entry))

    # open keypad
    def open_keypad(self, event, entry):
        self.keypads[f"{entry}"] = CustomKeypad(self, entry)
        self.keypads[f"{entry}"].create_keypad()

    # start the arduino thread
    def arduino_communication(self):   
        self.arduino_thread = ArduinoThread(self)
        self.arduino_thread.start_thread()

    # change mode
    def change_mode(self):
        if self.mode == "auto":
            self.mode = "manual"
            self.main_mode_label.configure(text="Manual Mode")
        elif self.mode == "manual":
            self.mode = "auto"
            self.main_mode_label.configure(text="Automatic Mode")
    
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
            self.auto_settings.geometry('%dx%d+%d+%d' % (self.w, self.h, self.x, self.y))

            # creating the widgets for the pop up screen and displaying them using a grid
            # mode and discription - will change for each mode
            self.mode_label = ctk.CTkLabel(self.auto_settings, text = "    Automatic    ", text_color="white")
            self.mode_label.grid(column=0, row=0, padx=5, pady=5, sticky="ew")
            self.description = ctk.CTkLabel(self.auto_settings, text = "DESCRIPTION", text_color="white")
            self.description.grid(column=0, row=1, padx=5, pady=10, sticky="ew")
            
            # spo2 inputs
            self.target_spo2_label = ctk.CTkLabel(self.auto_settings, text = "   Target Spo2   ", text_color="black", fg_color="#9eccf4", corner_radius=4, width=20)
            self.target_spo2_label.grid(column=0, row=3, padx=4, pady=10, sticky="ew")
            self.target_spo2_input = ctk.CTkEntry(self.auto_settings, width=100)
            self.target_spo2_input.grid(column=1, row=3, padx=4, pady=10, sticky="ew")
            self.bind_entry_to_keypad(self.target_spo2_input)
            
            self.min_spo2_label = ctk.CTkLabel(self.auto_settings, text = "    Min Spo2    ", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.min_spo2_label.grid(column=0, row=4, padx=4, pady=10, sticky="ew")
            self.min_spo2_input = ctk.CTkEntry(self.auto_settings, width=100)
            self.min_spo2_input.grid(column=1, row=4, padx=4, pady=10, sticky="ew")
            self.bind_entry_to_keypad(self.min_spo2_input)
            
            self.max_spo2_label = ctk.CTkLabel(self.auto_settings, text = "    Max Spo2    ", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.max_spo2_label.grid(column=0, row=5, padx=4, pady=10, sticky="ew")
            self.max_spo2_input = ctk.CTkEntry(self.auto_settings, width=100)
            self.max_spo2_input.grid(column=1, row=5, padx=4, pady=10, sticky="ew")
            self.bind_entry_to_keypad(self.max_spo2_input)
        
            # flow rate inputs
            self.init_flow_rate_label = ctk.CTkLabel(self.auto_settings, text = "Init Flow Rate", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.init_flow_rate_label.grid(column=2, row=3, padx=4, pady=10, sticky="ew")
            self.init_flow_rate_input = ctk.CTkEntry(self.auto_settings, width=100)
            self.init_flow_rate_input.grid(column=3, row=3, padx=4, pady=10, sticky="ew")
            self.bind_entry_to_keypad(self.init_flow_rate_input)
            
            self.min_flow_rate_label = ctk.CTkLabel(self.auto_settings, text = "Min Flow Rate", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.min_flow_rate_label.grid(column=2, row=4, padx=4, pady=10, sticky="ew")
            self.min_flow_rate_input = ctk.CTkEntry(self.auto_settings, width=100)
            self.min_flow_rate_input.grid(column=3, row=4, padx=4, pady=10, sticky="ew")
            self.bind_entry_to_keypad(self.min_flow_rate_input)
            
            self.max_flow_rate_label = ctk.CTkLabel(self.auto_settings, text = "Max Flow Rate", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.max_flow_rate_label.grid(column=2, row=5, padx=4, pady=10, sticky="ew")
            self.max_flow_rate_input = ctk.CTkEntry(self.auto_settings,  width=100)
            self.max_flow_rate_input.grid(column=3, row=5, padx=4, pady=10, sticky="ew")
            self.bind_entry_to_keypad(self.max_flow_rate_input)
            
            # pulse inputs
            self.min_pulse_label = ctk.CTkLabel(self.auto_settings, text = "    Min Pulse    ", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.min_pulse_label.grid(column=5, row=3, padx=4, pady=10, sticky="ew")
            self.min_pulse_input = ctk.CTkEntry(self.auto_settings, width=100)
            self.min_pulse_input.grid(column=6, row=3, padx=4, pady=10, sticky="ew")
            self.bind_entry_to_keypad(self.min_pulse_input)
            
            self.max_pulse_label = ctk.CTkLabel(self.auto_settings, text = "    Max Pulse    ", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.max_pulse_label.grid(column=5, row=4, padx=4, pady=10, sticky="ew")
            self.max_pulse_input = ctk.CTkEntry(self.auto_settings, width=100)
            self.max_pulse_input.grid(column=6, row=4, padx=4, pady=10, sticky="ew")
            self.bind_entry_to_keypad(self.max_pulse_input)

            # time interval for evaluaiton
            self.interval_label = ctk.CTkLabel(self.auto_settings, text = "       Interval      ", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.interval_label.grid(column=5, row=5, padx=4, pady=10, sticky="ew")
            self.interval_input = ctk.CTkEntry(self.auto_settings, width=100)
            self.interval_input.grid(column=6, row=5, padx=4, pady=10, sticky="ew")
            self.bind_entry_to_keypad(self.interval_input)

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

        # if it has already been created, open the screen
        else:
            self.auto_settings.deiconify()
    
    # save parameters for auto mode
    def save_auto_variables(self):
        # saves the inputted values in a dictionary
        parameters_full = False
        self.parameters = {}
        self.parameters['target_spo2_input'] = self.target_spo2_input.get()
        self.parameters['min_spo2_input'] = self.min_spo2_input.get()
        self.parameters['max_spo2_input'] = self.max_spo2_input.get()
        self.parameters['init_flow_rate_input'] = self.init_flow_rate_input.get()
        self.parameters['min_flow_rate_input'] = self.min_flow_rate_input.get()
        self.parameters['max_flow_rate_input'] = self.max_flow_rate_input.get()
        self.parameters['min_pulse_input'] = self.min_pulse_input.get()
        self.parameters['max_pulse_input'] = self.max_pulse_input.get()
        self.parameters['interval_input'] = self.interval_input.get()

        # check that all boxes have been filled (function currently off for testing)
        # if '' in self.parameters.values():
        #     self.error_message.configure(text="Must enter a value for each parameter!")
        # else:
        parameters_full = True
        self.error_message.configure(text="")
    
        # if there is input for each value, close settings window
        if parameters_full:
            # create the plots for monitoring control
            self.auto_plot()

            # calculate the % valve open
            self.valve_open_calculation(int(self.parameters['init_flow_rate_input']))
            # make an instance of the PIController
            self.pi_controller = PIController(self, Kp=0.5, Ki=0.1, sampling_time=int(self.parameters['interval_input']), target_spo2=int(self.parameters['target_spo2_input']))
            self.pi_controller.start_thread()

            # close settings window
            self.close_settings(self.auto_settings)

    # making plots for the spo2 and flowrate
    def auto_plot(self):
        # create the plots screen if it hasnt been created
        if self.control_plots is None:
            # creating the settings window as a pop up
            self.control_plots = ctk.CTkToplevel(self)
            # title and geomety of the settings screen
            self.control_plots.title("Control Plots")
            # self.control_plots.geometry('%dx%d+%d+%d' % (self.w, self.h, self.x, self.y))

            # create a single figure with two subplots
            self.control_fig, (self.control_spo2_ax, self.control_valve_ax) = plt.subplots(2, 1)

            # customize the spo2 subplot
            self.control_spo2_line, = self.control_spo2_ax.plot([], [], "#9eccf4")
            self.control_spo2_ax.set_title('Spo2')
            self.control_spo2_ax.set_xlabel('Time')
            self.control_spo2_ax.set_ylabel('Spo2')
            self.control_spo2_ax.set_xlim(0, 100)
            self.control_spo2_ax.set_ylim(-1, 1)

            # customize the valve subplot
            self.control_valve_line, = self.control_valve_ax.plot([], [], "#9eccf4")
            self.control_valve_ax.set_title('Valve % Open')
            self.control_valve_ax.set_xlabel('Time')
            self.control_valve_ax.set_ylabel('Valve Open')
            self.control_valve_ax.set_xlim(0, 100)
            self.control_valve_ax.set_ylim(0, 100)

            # adjust layout to prevent overlap
            plt.tight_layout()

            # display the figure
            self.control_canvas = FigureCanvasTkAgg(self.control_fig, master=self.control_plots)
            self.control_canvas.get_tk_widget().grid(column=0, row=0, columnspan=2, padx=10, pady=10)

            # widgets fitted properly to the window
            self.control_plots.grid_rowconfigure(0, weight=1)
            self.control_plots.grid_rowconfigure(1, weight=1)

        # if it has already been created, open the screen
        else:
            self.control_plots.deiconify()

        
    # value to update live plot
    def update_control_plot(self, spo2, valve_open):
        # clear the list if it's past 1000
        if len(self.control_live_spo2_list) < 100:
            pass
        else:
            self.control_live_spo2_list = []
            self.control_live_valve_list = []
        
        # add the new values to the lists
        self.control_live_spo2_list.append(spo2)
        self.control_live_valve_list.append(valve_open)
        
        # update the plot data
        self.control_spo2_line.set_xdata(range(len(self.control_live_spo2_list)))
        self.control_spo2_line.set_ydata(self.control_live_spo2_list)
        self.control_valve_line.set_xdata(range(len(self.control_live_valve_list)))
        self.control_valve_line.set_ydata(self.control_live_valve_list)

        # redraw the canvas
        self.control_canvas.draw()


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
            self.bind_entry_to_keypad(self.m_min_spo2_input)
            
            self.m_max_spo2_label = ctk.CTkLabel(self.manual_settings, text = "  Max Spo2  ", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.m_max_spo2_label.grid(column=0, row=4, padx=4, pady=10, sticky="ew")
            self.m_max_spo2_input = ctk.CTkEntry(self.manual_settings, width=100)
            self.m_max_spo2_input.grid(column=1, row=4, padx=4, pady=10, sticky="ew")
            self.bind_entry_to_keypad(self.m_max_spo2_input)
        
            # flow rate inputs
            self.m_set_flow_rate_label = ctk.CTkLabel(self.manual_settings, text = "  Flow Rate  ", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.m_set_flow_rate_label.grid(column=2, row=3, padx=4, pady=10, sticky="ew")
            self.m_set_flow_rate_input = ctk.CTkEntry(self.manual_settings, width=100)
            self.m_set_flow_rate_input.grid(column=3, row=3, padx=4, pady=10, sticky="ew")
            self.bind_entry_to_keypad(self.m_set_flow_rate_input)
            
            # pulse inputs
            self.m_min_pulse_label = ctk.CTkLabel(self.manual_settings, text = "    Min Pulse    ", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.m_min_pulse_label.grid(column=5, row=3, padx=4, pady=10, sticky="ew")
            self.m_min_pulse_input = ctk.CTkEntry(self.manual_settings, width=100)
            self.m_min_pulse_input.grid(column=6, row=3, padx=4, pady=10, sticky="ew")
            self.bind_entry_to_keypad(self.m_min_pulse_input)
            
            self.m_max_pulse_label = ctk.CTkLabel(self.manual_settings, text = "    Max Pulse    ", text_color="black", fg_color="#9eccf4", corner_radius=4)
            self.m_max_pulse_label.grid(column=5, row=4, padx=4, pady=10, sticky="ew")
            self.m_max_pulse_input = ctk.CTkEntry(self.manual_settings, width=100)
            self.m_max_pulse_input.grid(column=6, row=4, padx=4, pady=10, sticky="ew")
            self.bind_entry_to_keypad(self.m_max_pulse_input)

            # save button - sends the inputted values to the device and exits the self.manual_settings screen
            self.m_save_button = ctk.CTkButton(self.manual_settings, text = "SAVE", text_color="white", fg_color="#878788", corner_radius=4, command=self.save_manual_variables)
            self.m_save_button.grid(column=5, row=6, columnspan=2, pady=10, sticky="ew")

            # text box for error messages
            self.m_error_message = ctk.CTkLabel(self.manual_settings, text="", text_color="white")
            self.m_error_message.grid(column=1, row=6, columnspan=4, pady=10, sticky="ew")

            # widgets fitted properly to the window
            self.manual_settings.grid_columnconfigure(0, weight=1)
            self.manual_settings.grid_columnconfigure(1, weight=1)
            self.manual_settings.grid_columnconfigure(2, weight=1)
            self.manual_settings.grid_columnconfigure(3, weight=1)

        # if it has already been created, open the screen
        else:
            self.manual_settings.deiconify()

    # save parameters for manual mode
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
            self.m_error_message.configure(text="Must enter a value for each parameter!")
        else:
            parameters_full = True
            self.m_error_message.configure(text="")
            # testing writing to arduino
            self.arduino_thread.write_to_arduino(self.m_parameters['m_min_spo2_input'])
    
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