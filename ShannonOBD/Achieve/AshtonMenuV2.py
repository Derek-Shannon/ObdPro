#Base for switching to Settings

import tkinter as tk
from tkinter import ttk
import random, math, Gauge, os, obd, json


class MainScreen(tk.Frame):
    """The main dashboard screen with 4 gauges."""
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app = app_instance
        self.gauges = []
        self.gauges_index_in_data_list = []
        self.simulation_id = None
        self.setup_ui()
        
        self.query_output = [0] * len(self.app.data_list)
        self.last_query_output = [0] * len(self.app.data_list)
        self.moveTimer = [0] * len(self.app.data_list)
        self.movePower = [0] * len(self.app.data_list)

    def setup_ui(self):
        """Sets up the layout of the main screen."""
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

         # Create a container frame for the settings buttons
        button_container = tk.Frame(self)
        button_container.grid(row=0, column=2, sticky="ne", padx=5, pady=5)

        # Place the settings buttons within the new container frame
        settings_button = ttk.Button(button_container, text="⚙️ Settings",command=self.app.show_settings_screen)
        settings_button.pack(pady=5)
        
        settings_button2 = ttk.Button(button_container, text="⚙️ Settings", command=self.app.show_settings_screen)
        settings_button2.pack(pady=5)
        
        settings_button3 = ttk.Button(button_container, text="⚙️ Settings", command=self.app.show_settings_screen)
        settings_button3.pack(pady=5)
        
    def setup_gauges(self):
        """Updates the configuration of all gauges based on the app's state."""
        self.gauges.clear()
        self.gauges_index_in_data_list.clear()
        for i in range(4):
            gauge_name = self.app.gauge_type_selection[i]
            
            #finds the index of the name
            index_of_gauge = -1
            for j, data_object in enumerate(self.app.data_list):
                if data_object.name == gauge_name:
                    index_of_gauge = j
                    break
            gauge = Gauge.Gauge(self, **self.app.data_list[index_of_gauge].to_gauge_params())
            self.gauges.append(gauge)
            self.gauges_index_in_data_list.append(index_of_gauge)
            row = i // 2
            col = i % 2
            gauge.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
    def update_gauges(self, values):
        for index in range(len(self.gauges)):
            self.gauges[index].set_value(values[self.gauges_index_in_data_list[index]])
    def simulate_data(self):
        """Simulates data and updates the gauges periodically."""
        new_query_output = []
        for index in range(len(self.app.data_list)):
            self.moveTimer[index] -= 1
            if self.moveTimer[index] <= 0:
                self.moveTimer[index] = random.randint(1,8)
                full_range = self.app.data_list[index].max_value-self.app.data_list[index].min_value
                self.movePower[index] = random.randint(int(-full_range/10),int(full_range/10))
            value = self.last_query_output[index]+self.movePower[index]
            new_query_output.append(max(self.app.data_list[index].min_value, min(value, self.app.data_list[index].max_value)))

        self.last_query_output = new_query_output
        self.query_output = new_query_output
        self.update_gauges(self.query_output)
        
        # Call this function again after 100 milliseconds
        self.simulation_id = self.after(100, self.simulate_data)
    
    def start_simulation(self):
        """Starts the data simulation."""
        self.setup_gauges()
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
        active: bool = False
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
        self.active = active
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
        self.setup_ui()

    def setup_ui(self):
        """Sets up the layout of the settings screen."""
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
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
        save_button = ttk.Button(self, text="Save & Back", command=self.save_and_back)
        save_button.grid(row=4, column=0, columnspan=2, pady=20)
        
    def update_comboboxes(self):
        """Sets the current value of the comboboxes based on the app's state."""
        for i, combobox in enumerate(self.comboboxes):
            combobox.set(self.app.gauge_type_selection[i])

    def save_and_back(self):
        """Saves the new settings and returns to the main screen."""
        new_selections = [cb.get() for cb in self.comboboxes]
        self.app.gauge_type_selection = new_selections
        self.app.show_main_screen()

class App(tk.Tk):
    """The main application window."""
    def __init__(self):
        super().__init__()
        self.title("Customizable Gauges App")
        self.geometry("480x320")

        # Initial selection for the four gauges(should be changeable in future)
        self.gauge_type_selection = ["Spark_adv", "Rpm", "Engine_Load", "Intake_Temp"]
        
        # Create a container frame to manage screen switching
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Screen frames are initially None, they will be created as needed
        self.main_screen = None
        self.settings_screen = None
        
        #get data from Json
        self.data_list = []
        self.get_json_data()
        
        # Start by showing the main screen
        self.show_main_screen()

    def get_json_data(self):
        # Get the directory where the current script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(script_dir, 'input_data.json')

        # Load the JSON data
        with open(json_file_path, 'r', encoding="utf-8") as file:
            json_data = json.load(file)

        # Convert JSON to Data objects
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
    def show_main_screen(self):
        """Shows the main screen and hides the settings screen."""
        if self.settings_screen:
            self.settings_screen.pack_forget()
            
        if not self.main_screen:
            self.main_screen = MainScreen(self.container, self)
        
        self.main_screen.pack(fill="both", expand=True)
        self.main_screen.start_simulation()

    def show_settings_screen(self):
        """Shows the settings screen and hides the main screen."""
        if self.main_screen:
            self.main_screen.stop_simulation()
            self.main_screen.pack_forget()
        
        if not self.settings_screen:
            self.settings_screen = SettingsScreen(self.container, self)
        
        self.settings_screen.update_comboboxes()
        self.settings_screen.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()
