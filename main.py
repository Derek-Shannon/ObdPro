# ObdPro
# A customizable, real-time car dashboard application
# Derek Shannon
# Version: 2.0

import tkinter as tk
from tkinter import ttk
import random, math, os, obd, json, time, threading, Gauge

class MainScreen(tk.Frame):
    """The main dashboard screen with 4 gauges."""
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app = app_instance
        self.gauges = []
        self.gauges_index_in_data_list = []
        self.simulation_id = None
        self.images = []
        self.labels = []
        self.output_label = None
        
        self.base_lug_images = []
        self.scaled_lug_images = []

        self.setup_ui()
        
        self.query_output = [0] * len(self.app.data_list)
        self.last_query_output = [0] * len(self.app.data_list)
        self.moveTimer = [0] * len(self.app.data_list)
        self.movePower = [0] * len(self.app.data_list)
        
        self.fps = 30
        self.set_theme(self.app.current_theme)

    def setup_ui(self):
        """Sets up the layout of the main screen."""
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Create a container frame for the settings buttons
        self.side_container = tk.Frame(self)
        self.side_container.grid(row=0, column=2, rowspan=2,sticky="ne", padx=0, pady=5)

        # Place the settings buttons within the new container frame
        self.settings_button = tk.Button(self.side_container, text="⚙️ Settings",command=self.app.show_settings_screen)
        self.settings_button.pack(pady=5)
        
        # Button to reset min/max
        self.reset_min_max_button = tk.Button(self.side_container, text="↻ Min/Max", command=self.reset_min_max)
        self.reset_min_max_button.pack(pady=1)
        
        #gif lug warning
        try:
            # Store the original images
            self.base_lug_images.append(tk.PhotoImage(file=os.path.join(self.app.script_dir, "assets/images/lugWarningGrey.png")))
            self.base_lug_images.append(tk.PhotoImage(file=os.path.join(self.app.script_dir, "assets/images/lugWarning.png")))
            self.base_lug_images.append(tk.PhotoImage(file=os.path.join(self.app.script_dir, "assets/images/lugWarningGreen.png")))
            
            # Create a Label widget to display the image
            self.labels.append(tk.Label(self.side_container, image=self.base_lug_images[1]))
            self.labels[0].pack(padx=0, pady=1)
            
        except tk.TclError:
            print("Error loading image. Make sure 'my_image.gif' exists and is a valid GIF file.")
        
        self.bottom_container = tk.Frame(self)
        self.bottom_container.grid(row=3, column=0, columnspan=2, padx=15, pady=10, sticky="w")
        self.output_label = ttk.Label(self.bottom_container, text=f"\n\n")
        self.output_label.pack()

    def set_theme(self, theme):
        """Applies the current theme to the MainScreen and all its widgets."""
        bg_color = self.app.theme[theme]['frame_bg']
        text_color = self.app.theme[theme]['text']
        
        self.configure(bg=bg_color)
        
        # Configure styles for ttk widgets
        style = ttk.Style()
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=text_color)
        #style.configure("TButton", background=bg_color)
        
        self.side_container.configure(bg=bg_color)
        self.bottom_container.configure(bg=bg_color)
        self.output_label.configure(background=bg_color, foreground=text_color)
        
         # This is the new line you need to add or update
        if self.labels:
            self.labels[0].configure(background=self.side_container.cget("bg"))
        
        for gauge in self.gauges:
            gauge.set_theme(theme)

    def setup_gauges(self):
        """Updates the configuration of all gauges based on the app's state."""
        self.gauges.clear()
        self.gauges_index_in_data_list.clear()
        
        # First, remove any existing gauges from the grid
        for widget in self.winfo_children():
            if isinstance(widget, Gauge.Gauge):
                widget.destroy()

        for i in range(4):
            gauge_name = self.app.gauge_type_selection[i]
            
            #finds the index of the name
            index_of_gauge = -1
            for j, data_object in enumerate(self.app.data_list):
                if data_object.name == gauge_name:
                    index_of_gauge = j
                    break
            
            # Pass the scale factor to the Gauge constructor
            gauge = Gauge.Gauge(self, scale_factor=self.app.gauge_scale, **self.app.data_list[index_of_gauge].to_gauge_params())
            self.gauges.append(gauge)
            self.gauges_index_in_data_list.append(index_of_gauge)
            row = i // 2
            col = i % 2
            gauge.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        
        # Re-scale the lug images
        self.scale_lug_images(self.app.gauge_scale)

        self.set_theme(self.app.current_theme)

    def scale_lug_images(self, scale):
        """Scales the lug warning images based on the scale factor."""
        # Clear the scaled images list
        self.scaled_lug_images = []
        
        # Scale each base image and add it to the scaled list
        for image in self.base_lug_images:
            width = int(image.width() * scale)
            height = int(image.height() * scale)
            # Use subsample to scale the image. Note: PhotoImage.subsample() only works for integer scaling.
            # A more robust solution for fractional scaling would involve an external library like Pillow (PIL).
            # For this example, let's assume integer scaling for simplicity, but you may need to adjust this.
            if scale >= 1:
                self.scaled_lug_images.append(image.zoom(int(scale)))
            else:
                self.scaled_lug_images.append(image.subsample(int(1/scale)))
        
        # Update the image on the label
        if self.labels:
            self.labels[0].config(image=self.scaled_lug_images[0])
            self.check_lug_warning() # Update the image to the correct state

    def reset_min_max(self):
        for gauge in self.gauges:
            gauge.resetMinMax()
    
    def update_gauges(self, values):
        for index in range(len(self.gauges)):
            self.gauges[index].set_value(values[self.gauges_index_in_data_list[index]])
    
    def simulate_test_data(self):
        """Simulates data and updates the gauges periodically."""
        new_query_output = []
        for index in range(len(self.app.data_list)):
            self.moveTimer[index] -= 1
            if self.moveTimer[index] <= 0:
                self.moveTimer[index] = random.randint(5*self.fps/10,10*self.fps/10)
                full_range = self.app.data_list[index].max_value-self.app.data_list[index].min_value
                self.movePower[index] = random.uniform(-full_range / self.fps, full_range / self.fps)
            if self.last_query_output[index] == self.app.data_list[index].max_value or self.last_query_output[index] == self.app.data_list[index].min_value:
                self.movePower[index] = -self.movePower[index]
            value = self.last_query_output[index]+self.movePower[index]
            new_query_output.append(max(self.app.data_list[index].min_value, min(value, self.app.data_list[index].max_value)))
            
        self.last_query_output = new_query_output
        self.query_output = new_query_output
        self.update_gauges(self.query_output)
        self.check_lug_warning()
        
        self.app.output.update()
        # Call this function again after 100 milliseconds
        self.simulation_id = self.after(int(1000/self.fps), self.simulate_test_data)
    
    def check_lug_warning(self):
        engine_load = 0
        rpm = 0
        for index in range(len(self.app.data_list)):
            if self.app.data_list[index].name == "Rpm":
                rpm = self.query_output[index]
            if self.app.data_list[index].name == "Engine_Load":
                engine_load = self.query_output[index]
        
        #lugging
        if engine_load>30 and rpm<2000:
            self.labels[0].configure(image=self.scaled_lug_images[1])
        #coasting
        elif engine_load<25 and rpm<2500 and rpm>1800:
            self.labels[0].configure(image=self.scaled_lug_images[2])
        else:
            self.labels[0].configure(image=self.scaled_lug_images[0])
            
    def simulate_data(self):
        if self.app.obdPro.connected:
            self.app.obdPro.update_data()
            self.query_output = self.app.obdPro.getQueryOutput()
            self.update_gauges(self.query_output)
            self.check_lug_warning()
            
        self.app.output.update()
        # Call this function again after 100 milliseconds
        self.simulation_id = self.after(int(1000/self.fps), self.simulate_data)
    
    def start_simulation(self):
        """Starts the data simulation."""
        self.setup_gauges()
        if self.app.inDebugMode:
            self.simulate_test_data()
        else:
            self.simulate_data()

    def stop_simulation(self):
        """Stops the data simulation."""
        if self.simulation_id:
            self.after_cancel(self.simulation_id)
            self.simulation_id = None
            
class Data:
    def __init__(
        self,
        name: str,
        query_reference,
        unit: str,
        blue: int = 0,
        light_blue: int = 0,
        yellow: int = 0,
        red: int = 0,
        min_value: int = 0,
        max_value: int = 100,
    ):
        self.name = name
        self.query_reference = query_reference
        self.unit = unit
        self.blue = blue
        self.light_blue = light_blue
        self.yellow = yellow
        self.red = red
        self.min_value = min_value
        self.max_value = max_value
    def to_gauge_params(self):
        #Converts Data attributes to a dictionary compatible with Gauge initialization.
        return {
            "label": self.name,
            "unit": self.unit,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "blue": self.blue,
            "light_blue": self.light_blue,
            "yellow": self.yellow,
            "red": self.red,
        }

class SettingsScreen(tk.Frame):
    """The settings screen for configuring the gauges."""
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app = app_instance
        self.comboboxes = []

        # Add a new variable for the slider value
        self.scale_value = tk.DoubleVar(value=self.app.gauge_scale)

        self.setup_ui()
        self.set_theme(self.app.current_theme)

    def setup_ui(self):
        """Sets up the layout of the settings screen."""
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        
        # Dropdown options from the App's configs
        options = []
        for data in self.app.data_list:
            options.append(data.name)

        # Create a dropdown for each of the four gauges
        for i in range(4):
            label = ttk.Label(self, text=f"Gauge {i+1} Type:")
            label.grid(row=i, column=0, padx=10, pady=10, sticky="e")
            
            combobox = ttk.Combobox(self, values=options)
            combobox.current(i)  # Set initial selection
            combobox.grid(row=i, column=1, padx=10, pady=10, sticky="w")
            self.comboboxes.append(combobox)
            
        # Button to save settings and go back
        save_button = tk.Button(self, text="Save & Back", command=self.save_and_back)
        save_button.grid(row=4, column=0, columnspan=2, pady=5)
        
        
        self.bottom_container = ttk.Frame(self, border=2,borderwidth=2,relief=tk.SUNKEN)
        self.bottom_container.grid(row=5, column=0, columnspan=2, padx=15, pady=10, sticky="w")
        
        # Add a label and a slider for the gauge size
        self.size_label = ttk.Label(self.bottom_container, text=f"Gauge Size: {self.scale_value.get():.2f}")
        self.size_label.grid(row=0, column=3, padx=0, pady=10, sticky="w")

        self.size_slider = ttk.Scale(self.bottom_container, from_=0.75, to=4.0, orient=tk.HORIZONTAL, variable=self.scale_value)
        self.size_slider.grid(row=1, column=3, padx=0, pady=10, sticky="w")
        self.size_slider.bind("<Motion>", self.update_size_label) # Add this line to update the label in real-time.

        label = ttk.Label(self.bottom_container, text=f"Extras: ")
        label.grid(row=0,column=0,rowspan=2, padx=10, pady=10)
        # Button to enable random numbers
        self.debug_button = tk.Button(self.bottom_container, text="Disable Debug" if self.app.inDebugMode else "Enable Debug", command=self.on_click_debug_button)
        self.debug_button.grid(row=0,column=1, pady=10)
        
        # Button to toggle theme
        self.theme_button = tk.Button(self.bottom_container, text="Dark Mode", command=self.app.toggle_theme)
        self.theme_button.grid(row=1,column=1, pady=10)
        
        #refresh car connection button
        self.reconnect_button = tk.Button(self.bottom_container, text="Reconnect", command=self.app.obdPro.start_connection)
        self.reconnect_button.grid(row=0,column=2)
        
        #Fullscreen button
        self.fullscreen_button = tk.Button(self.bottom_container, text="Toggle Fullscreen", command=self.app.toggle_fullscreen)
        self.fullscreen_button.grid(row=1,column=2)
    def update_size_label(self, event):
        """Updates the label text with the current slider value."""
        self.size_label.config(text=f"Gauge Size: {self.scale_value.get():.2f}")
        
    def on_click_debug_button(self):
        if self.app.inDebugMode:
            self.debug_button.config(text="Enable Debug")
            self.app.inDebugMode = False
            print("Disabled")
        else:
            self.debug_button.config(text="Disable Debug")
            self.app.inDebugMode = True
            print("Enabled")
    
    def set_theme(self, theme):
        bg_color = self.app.theme[theme]['frame_bg']
        text_color = self.app.theme[theme]['text']
        
        self.configure(bg=bg_color)
        
        # Configure styles for ttk widgets
        style = ttk.Style()
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=text_color)
        #style.configure("TButton", background=bg_color)
        
        if theme == 'dark':
            self.theme_button.config(text="Light Mode")
        else:
            self.theme_button.config(text="Dark Mode")
    
    def update_comboboxes(self):
        """Sets the current value of the comboboxes based on the app's state."""
        for i, combobox in enumerate(self.comboboxes):
            combobox.set(self.app.gauge_type_selection[i])

    def save_and_back(self):
        """Saves the new settings and returns to the main screen."""
        new_selections = [cb.get() for cb in self.comboboxes]
        self.app.gauge_type_selection = new_selections

        self.app.gauge_scale = self.scale_value.get()

        #save
        self.app.save_json_data()
        self.app.show_main_screen()
        print("Saved")

class App(tk.Tk):
    """The main application window."""
    def __init__(self):
        super().__init__()
        self.title("Shannon's Obd Pro")
        self.geometry("480x320")
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

        # Theme definitions
        self.theme = {
            'light': {
                'frame_bg': 'lightgrey',
                'canvas_bg': 'lightgrey',
                'inner_bg': 'white',
                'text': 'black',
                'outline': '#343434'
            },
            'dark': {
                'frame_bg': "#000000",
                'canvas_bg': "#000000",
                'inner_bg': "#000000",
                'text': '#F0F0F0',
                'outline': '#FFFFFF'
            }
        }

        self.gauge_scale = 1.0
        self.gauge_type_selection = ["Spark_adv", "Rpm", "Engine_Load", "Intake_Temp"]
        
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.main_screen = None
        self.settings_screen = None
        
        self.output = Output(self)
        
        self.inDebugMode = True
        self.inDarkMode = False
        self.current_theme = 'light'
        
        self.get_json_data()
        
        self.obdPro = ObdPro(self)
        
        self.show_main_screen()
        self.set_theme()

    def set_theme(self):
        """Updates the theme for the entire app."""
        self.current_theme = 'dark' if self.inDarkMode else 'light'
        bg_color = self.theme[self.current_theme]['frame_bg']
        self.configure(bg=bg_color)
        self.container.configure(bg=bg_color)
        
        if self.main_screen:
            self.main_screen.set_theme(self.current_theme)
        if self.settings_screen:
            self.settings_screen.set_theme(self.current_theme)
            
    def set_output_text(self, text):
        if self.main_screen == None:
            print("Error! No Display available")
        else:
            self.output.add(text)
            
    def get_json_data(self):
        json_file_path = os.path.join(self.script_dir, 'assets/data/input_data.json')
        with open(json_file_path, 'r', encoding="utf-8") as file:
            json_data = json.load(file)
        self.data_list = [
            Data(
                name=item["name"],
                query_reference=getattr(obd.commands, item["query_reference"]),
                unit=item["unit"],
                min_value=item["min_value"],
                max_value=item["max_value"],
                blue=item.get("blue", -9999),
                light_blue=item.get("light_blue", -9999),
                yellow=item.get("yellow", 9999),
                red=item.get("red", 9999)
            )
            for item in json_data
        ]
        saves_json_path = os.path.join(self.script_dir, 'assets/data/save_data.json')
        try:
            with open(saves_json_path, 'r', encoding="utf-8") as file:
                content = file.read().strip()
                if not content:
                    print("File content is empty.")
                    json_data = {}
                else:
                    json_data = json.loads(content)
                    self.gauge_type_selection = json_data['gauge_type_selection']
                    self.inDebugMode = json_data['inDebugMode']
                    self.inDarkMode = json_data['inDarkMode']
                    self.attributes('-fullscreen', json_data['inFullscreen'])
                    self.gauge_scale = json_data.get('gauge_scale', 1.0)
        except FileNotFoundError:
            print(f"Error: The file {saves_json_path} was not found.")
            
    def save_json_data(self):
        saves_json_path = os.path.join(self.script_dir, 'assets/data/save_data.json')
        formatted_save_data = {
            "gauge_type_selection": self.gauge_type_selection,
            "inDebugMode": self.inDebugMode,
            "inDarkMode": self.inDarkMode,
            "inFullscreen": self.attributes('-fullscreen'),
            "gauge_scale": self.gauge_scale
        }
        print(formatted_save_data)
        with open(saves_json_path, 'w') as json_file:
            json.dump(formatted_save_data, json_file, indent=4)
        
    def show_main_screen(self):
        if self.settings_screen:
            self.settings_screen.pack_forget()
            
        if not self.main_screen:
            self.main_screen = MainScreen(self.container, self)
        
        self.main_screen.pack(fill="both", expand=True)
        self.set_theme()
        
        if not self.inDebugMode and not self.obdPro.connected:
            self.obdPro.start_connection()
        self.main_screen.start_simulation()

    def show_settings_screen(self):
        if self.main_screen:
            self.main_screen.stop_simulation()
            self.main_screen.pack_forget()
        
        if not self.settings_screen:
            self.settings_screen = SettingsScreen(self.container, self)
        
        self.settings_screen.update_comboboxes()
        self.settings_screen.pack(fill="both", expand=True)
        self.set_theme()
    
    def toggle_theme(self):
        self.inDarkMode = not self.inDarkMode
        self.set_theme()
    def toggle_fullscreen(self):
        is_fullscreen = self.attributes('-fullscreen')
        self.attributes('-fullscreen', not is_fullscreen)

class ObdPro:
    def __init__(self, app):
        self.app = app
        self.port = "/dev/ttyUSB0"
        self.connection = None
        self.connected = False
        self.names = []
        self.queryReferences = []
        self.queryOutput = [0] * 10
        self.thread = threading.Thread(target=self.connect)
        
    def start_connection(self):
        if not self.thread.is_alive():
            self.thread = threading.Thread(target=self.connect)
            self.thread.start()
        else:
            self.app.set_output_text("Already Trying to Connect...")
            
    def connect(self):
        while True:
            if self.app.inDebugMode:
                break
            self.connected = False
            try:
                self.connection = obd.OBD(self.port)
                if self.connection.is_connected():
                    self.app.set_output_text("Connected to Vehicle!")
                    self.connected = True
                    break
                else:
                    self.app.set_output_text("Not connected, retrying...")
            except Exception as e:
                self.app.set_output_text(f"Error connecting: {e}, retrying...")
            time.sleep(2)

        self.names = []
        self.queryReferences = []
        for data in self.app.data_list:
            self.addValue(data.name, data.query_reference)

    def addValue(self, name: str, queryReference):
        #test open values
        if self.connection.supports(queryReference):
            self.names.append(name)
            self.queryReferences.append(queryReference)
        else:
            print("Car")
    def convert_to_standard_units(self, index, value):
        if self.names[index] == "Speed":
            return int(value * 0.621371)
        elif self.names[index] in ["Intake_Temp", "Ambiant_Temp", "Coolant_temp"]:
            return int(value * 9 / 5 + 32)
        elif self.names[index] == "MAF":
            return int(value * 0.132277)
        elif self.names[index] == "Boost":
            return int(value * 0.1450377377)
        return int(value)

    def update_data(self):
        for i, cmd in enumerate(self.queryReferences):
            result = self.connection.query(cmd)
            if result is None or result.is_null():
                self.queryOutput[i] = 0
            else:
                value = result.value.magnitude if hasattr(result.value, 'magnitude') else result.value
                self.queryOutput[i] = self.convert_to_standard_units(i, value)
        return "   ".join(map(str, self.queryOutput))

    def getQueryOutput(self):
        return self.queryOutput

class Output:
    def __init__(self, app):
        self.DWELL_TIME = 5
        self.TEXT_ROWS = 3
        
        self.app = app
        
        self.text_list = []
        self.last_text_time = []
        self.message_count = 0
        
        self.affirmation_time = time.time()
        
    def add(self, text):
        self.message_count += 1
        self.text_list.insert(0, str(self.message_count)+": "+text)
        self.last_text_time.insert(0, time.time())
        if len(self.text_list) > self.TEXT_ROWS:
            self.text_list.pop()
            
    def update(self):
        if self.affirmation_time+60 < time.time():
            #self.add("Thanks for using ObdPro by ShannonSoftware!")
            self.affirmation_time = time.time()
        if len(self.text_list) == 0:
            return
        
        remove_quantity = 0
        for a_time in self.last_text_time:
            if a_time+self.DWELL_TIME < time.time():
                remove_quantity +=1
        for i in range(remove_quantity):
            self.text_list.pop()
            self.last_text_time.pop()
        
        self.__display()
        
    def __display(self):
        out = ""
        for i in range(self.TEXT_ROWS-len(self.text_list)):
            out +="\n"
        for i in range(len(self.text_list)):
            out += self.text_list[len(self.text_list)-1-i] + "\n"
        out= out[:-1]
        
        self.app.main_screen.output_label.config(text=f"{out}")
        
if __name__ == "__main__":
    app = App()
    app.mainloop()