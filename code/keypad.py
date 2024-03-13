# import for custom tkinter
import customtkinter as ctk
import tkinter as tk

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
        self.h = 220
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
            '.', '0', 'Clear',
            'Enter'
        ]

        # create buttons
        row = 1
        col = 0
        for button_text in buttons:
            button = ctk.CTkButton(self.keypad_frame, text=button_text, command=lambda text=button_text: self.on_button_click(text), text_color="white", fg_color="#878788", corner_radius=4)
            if button_text == 'Enter':
                button.grid(row=row, column=col, columnspan=3, padx=5, pady=5)  # span across 3 columns
            else:
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
