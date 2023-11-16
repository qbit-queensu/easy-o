import customtkinter as ctk

# app theme
ctk.set_default_color_theme('dark-blue')

# main window of the UI
class MainWindow(ctk.CTk):

# init function, the function that will be run automatically
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # title and geometry of the main wndow
        self.title("easy o UI")    
        self.geometry("700x425")    

        # creating all the widgets for the main window and displaying them in using a grid
        # mode
        self.mode_label = ctk.CTkLabel(self, text="MODE", text_color="white", fg_color="#878788", corner_radius=4)
        self.mode_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # placeholder 1
        self.ph1_label = ctk.CTkLabel(self, text="")
        self.ph1_label.grid(row=1, column=0, padx=10, pady=30, sticky="ew")
        # placeholder 2
        self.ph2_label = ctk.CTkLabel(self, text="")
        self.ph2_label.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        # placeholder 3
        self.ph3_label = ctk.CTkLabel(self, text="")
        self.ph3_label.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        # placeholder 4
        self.ph4_label = ctk.CTkLabel(self, text="")
        self.ph4_label.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

        # settings
        self.setting_button = ctk.CTkButton(self, text="SETTINGS", text_color="white", fg_color="#878788", corner_radius=4)
        self.setting_button.grid(row=0, column=4, padx=10, pady=10, sticky="ew")

        # spo2
        self.spo2_label = ctk.CTkLabel(self, text="spo2", text_color="black", fg_color="#9eccf4", corner_radius=4)
        self.spo2_label.grid(row=2, column=0, padx=10, pady=20, sticky="ew")
        # flow rate
        self.fr_label = ctk.CTkLabel(self, text="flow rate", text_color="black", fg_color="#9eccf4", corner_radius=4)
        self.fr_label.grid(row=3, column=0, padx=10, pady=20, sticky="ew")
        # pulse
        self.fr_label = ctk.CTkLabel(self, text="pulse", text_color="black", fg_color="#9eccf4", corner_radius=4)
        self.fr_label.grid(row=4, column=0, padx=10, pady=20, sticky="ew")

        # spo2 graph
        self.spo2_graph = ctk.CTkLabel(self, text="spo2", text_color="white", fg_color="#9eccf4", corner_radius=4)
        self.spo2_graph.grid(row=2, column=1, columnspan=4, rowspan=4, padx=10, pady=20, sticky="ew")


        # widgets move with he window
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
 
 
if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()