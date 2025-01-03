import math
import tkinter as tk
import obd  # Make sure obd library is installed
import time
import random

class CarDashboard(tk.Tk):
    def __init__(self, names, values, ranges, units):
        super().__init__()
        self.title("Car Dashboard")
        self.geometry("850x600")

        self.gauge_titles = names
        self.gauge_ranges = ranges
        self.gauge_units = units
        self.gauge_values = values 

        # Lists to store maximum and minimum values for each gauge
        self.max_values = values.copy()
        self.min_values = values.copy()

        self.gauges = []
        for i, title in enumerate(self.gauge_titles):
            self.create_gauge2(i, title)

        # Add a Reset button
        reset_button = tk.Button(self, text="Reset Max/Min", command=self.reset_values)
        reset_button.grid(column=0, row=0)

    def create_gauge(self, index, title):
        frame = tk.Frame(self)
        frame.grid(column=index-index%2, row=index%2)

        label = tk.Label(frame, text=title)
        label.pack()

        canvas = tk.Canvas(frame, width=30, height=200)
        canvas.pack()

        canvas.create_rectangle(0, 0, 30, 200, fill="gray", outline="gray")

        value = self.gauge_values[index]
        min_value, max_value, change1, change2 = self.gauge_ranges[index]

        colored_height = self.scale_value(value, min_value, max_value, 200)
        color = self.get_gauge_color(value, change1, change2)
        canvas.create_rectangle(0, 200 - colored_height, 30, 200, fill=color, outline=color)

        value_label = tk.Label(frame, text=f"{value} {self.gauge_units[index]}")
        value_label.pack()

        # Create labels to show max and min values
        max_value_label = tk.Label(frame, text=f"Max: {value} {self.gauge_units[index]}")
        max_value_label.pack()

        min_value_label = tk.Label(frame, text=f"Min: {value} {self.gauge_units[index]}")
        min_value_label.pack()

        # Store the canvas, value label, max and min value labels
        self.gauges.append((canvas, value_label, max_value_label, min_value_label))

    def scale_value(self, value, min_value, max_value, height):
        if value < min_value:
            return 0
        if value > max_value:
            return height
        return ((value - min_value) / (max_value - min_value)) * height

    def get_gauge_color(self, value, min_value, max_value):
        if value < min_value:
            return "blue"
        elif value > max_value:
            return "red"
        else:
            return "green"

    def update_gauge(self, values):
        for index in range(len(self.gauge_titles)):
            self.gauge_values[index] = values[index]
            canvas, value_label, max_value_label, min_value_label = self.gauges[index]

            min_value, max_value, change1, change2 = self.gauge_ranges[index]
            colored_height = self.scale_value(values[index], min_value, max_value, 200)
            color = self.get_gauge_color(values[index], change1, change2)

            canvas.coords(canvas.find_all()[1], 0, 200 - colored_height, 30, 200)
            canvas.itemconfig(canvas.find_all()[1], fill=color)

            value_label.config(text=f"{values[index]} {self.gauge_units[index]}")

            # Update max and min values
            if values[index] > self.max_values[index]:
                self.max_values[index] = values[index]
                max_value_label.config(text=f"Max: {self.max_values[index]} {self.gauge_units[index]}")

            if values[index] < self.min_values[index]:
                self.min_values[index] = values[index]
                min_value_label.config(text=f"Min: {self.min_values[index]} {self.gauge_units[index]}")

    def reset_values(self):
        # Reset max and min values to the current values
        self.max_values = self.gauge_values.copy()
        self.min_values = self.gauge_values.copy()

        # Update the labels to reflect the reset
        for index, (_, _, max_value_label, min_value_label) in enumerate(self.gauges):
            max_value_label.config(text=f"Max: {self.gauge_values[index]} {self.gauge_units[index]}")
            min_value_label.config(text=f"Min: {self.gauge_values[index]} {self.gauge_units[index]}")

class ObdPro:
    def __init__(self):
        self.port = "/dev/ttyUSB0"
        self.connection = None
        self.connect()

        self.names = []
        self.querryReferences = []
        self.querryOutput = [0] * 8  # Initializing with zeroes

    def connect(self):
        while True:
            try:
                # Attempt to connect to the OBD-II device
                self.connection = obd.OBD(self.port)  # Adjust port for Windows
                if self.connection.is_connected():
                    print("Connected to OBD-II device.")
                    break
                else:
                    print("Not connected, retrying...")
            except Exception as e:
                print(f"Error connecting: {e}, retrying...")
            time.sleep(2)

    def addValue(self, name: str, querryReference):
        self.names.append(name)
        self.querryReferences.append(querryReference)

    def convert_to_standard_units(self, index, value):
        if self.names[index] == "Speed":
            return int(value * 0.621371)
        elif self.names[index] in ["Intake_Temp", "Ambiant_Air_Temp", "Coolant_temp"]:
            return int(value * 9 / 5 + 32)
        elif self.names[index] == "MAF":
            return int(value * 0.132277)
        return int(value)

    def _getDataString(self):
        for i, cmd in enumerate(self.querryReferences):
            result = self.connection.query(cmd)
            if result is None or result.is_null():
                self.querryOutput[i] = 0
            else:
                value = result.value.magnitude if hasattr(result.value, 'magnitude') else result.value
                self.querryOutput[i] = self.convert_to_standard_units(i, value)
        return "   ".join(map(str, self.querryOutput))

    def getQuerryOutput(self):
        return self.querryOutput

    def displayLoop(self, app):
        self._getDataString()
        app.update_gauge(self.getQuerryOutput())
        app.after(100, self.displayLoop, app)
class FakeObdPro:
    def __init__(self):
        self.names = [
            "Speed", "Rpm", "Engine_Load", "MAF", 
            "Intake_Temp", "Ambiant_Air_Temp", "Coolant_temp", "Spark_adv"
        ]
        self.querryOutput = [0] * len(self.names)
        self.frame_counter = 0

    def generate_fake_data(self):
        self.querryOutput = [
            random.randint(0, 135),        # Speed in mph
            random.randint(0, 7500),       # RPM
            random.randint(0, 100),        # Engine Load %
            random.randint(0, 100),        # MAF in lbs/min
            random.randint(-40, 100),      # Intake Temperature °F
            random.randint(-4, 122),       # Ambient Air Temperature °F
            random.randint(14, 212),       # Coolant Temperature °F
            random.randint(0, 50),         # Spark Advance degrees
        ]

    def getQuerryOutput(self):
        self.generate_fake_data()
        return self.querryOutput

    def displayLoop(self, app):
        # Increment the frame counter
        self.frame_counter += 1

        # Check if the frame counter is a multiple of 10
        if self.frame_counter % 10 == 0:
            app.update_gauge(self.getQuerryOutput())

        # Continue the loop with a delay
        app.after(100, self.displayLoop, app)

if __name__ == "__main__":
    obdPro = None
    if True:
        obdPro = FakeObdPro()
    else:
        obdPro = ObdPro()
        obdPro.addValue("Speed", obd.commands.SPEED)
        obdPro.addValue("Rpm", obd.commands.RPM)
        obdPro.addValue("Engine_Load", obd.commands.ENGINE_LOAD)
        obdPro.addValue("MAF", obd.commands.MAF)
        obdPro.addValue("Intake_Temp", obd.commands.INTAKE_TEMP)
        obdPro.addValue("Ambiant_Air_Temp", obd.commands.AMBIANT_AIR_TEMP)
        obdPro.addValue("Coolant_temp", obd.commands.COOLANT_TEMP)
        obdPro.addValue("Spark_adv", obd.commands.TIMING_ADVANCE)
    
    ranges = [
        #(min, max, change1, change2)
        (0, 135, 0, 135),
        (0, 7500, 2000, 5000),
        (0, 100, 0, 80),
        (0, 100, 0, 100),
        (-40, 100, 0, 70),
        (-40, 122, 0, 80),
        (-40, 212, 80, 110),
        (0, 50, 0, 50),
    ]
    units = ["mph", "RPM", "%", "lbs/min", "°F", "°F", "°F", "degrees"]
    
    app = CarDashboard(obdPro.names, obdPro.getQuerryOutput(), ranges, units)
    obdPro.displayLoop(app)
    app.mainloop()
