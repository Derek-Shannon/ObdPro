import tkinter as tk
import obd
import time

class CarDashboard(tk.Tk):
    def __init__(self, names, values, ranges, units):
        super().__init__()
        self.title("Car Dashboard")
        self.geometry("800x400")

        # List of labels for the gauge titles
        self.gauge_titles = names
        
        # List of value ranges for each gauge (min, max)
        self.gauge_ranges = ranges
        
        # Units for each gauge (e.g., mph, °F, etc.)
        self.gauge_units = units
        
        # Initial values for the gauges
        self.gauge_values = values

        # Create vertical bars (gauges)
        self.gauges = []
        for i, title in enumerate(self.gauge_titles):
            self.create_gauge(i, title)

    def create_gauge(self, index, title):
        # Create a frame for each gauge
        frame = tk.Frame(self)
        frame.pack(side="left", padx=10)

        # Create the label for the gauge
        label = tk.Label(frame, text=title)
        label.pack()

        # Create a canvas to draw the gauge as a colored vertical bar
        canvas = tk.Canvas(frame, width=30, height=200)
        canvas.pack()

        # Draw the background (gray bar) for the gauge
        canvas.create_rectangle(0, 0, 30, 200, fill="gray", outline="gray")
        
        # Get value and range
        value = self.gauge_values[index]
        min_value, max_value, change1, change2 = self.gauge_ranges[index]
        
        # Scale the value to fit within the gauge height
        colored_height = self.scale_value(value, min_value, max_value, 200)
        
        # Draw the colored bar (the gauge)
        color = self.get_gauge_color(value, change1, change2)
        canvas.create_rectangle(0, 200 - colored_height, 30, 200, fill=color, outline=color)

        # Create a label to display the value next to the colored bar
        value_label = tk.Label(frame, text=f"{value} {self.gauge_units[index]}")
        value_label.pack()

        # Store the canvas and label for later updates
        self.gauges.append((canvas, value_label))

    def scale_value(self, value, min_value, max_value, height):
        # Scale the value between min_value and max_value to a height value (0 to height)
        if value < min_value:
            return 0
        if value > max_value:
            return height
        return ((value - min_value) / (max_value - min_value)) * height

    def get_gauge_color(self, value, min_value, max_value):
        # Simple color logic: green for normal, yellow for near max, red for too high
        if value < min_value:
            return "blue"  # Below normal
        elif value > max_value:
            return "red"  # Above normal
        else:
            return "green"  # Normal range

    def update_gauge(self, values):
        # Update the gauge value and color based on the value
        for index in range(len(self.gauge_titles)):
            self.gauge_values[index] = values[index]
            canvas, value_label = self.gauges[index]

            # Get the range for this gauge
            min_value, max_value, change1, change2 = self.gauge_ranges[index]

            # Scale the height and color based on the value
            colored_height = self.scale_value(values[index], min_value, max_value, 200)
            color = self.get_gauge_color(values[index], change1, change2)

            # Update the gauge bar color and height
            canvas.coords(canvas.find_all()[1], 0, 200 - colored_height, 30, 200)  # Update the colored bar height
            canvas.itemconfig(canvas.find_all()[1], fill=color)  # Update the color
            
            # Update the value label with units
            value_label.config(text=f"{values[index]} {self.gauge_units[index]}")

class ObdPro:
    def __init__(self):
        self.port = "/dev/ttyUSB0"
        self.connection = None
        self.connect()

        self.f = open("output.txt", "a")
        self.names = []
        self.querryReferences = []
        self.querryOutput = []  # List for sensor data

    def connect(self):
        while True:
            try:
                # Attempt to connect to the OBD-II device
                self.connection = obd.OBD(self.port)  # Adjust port for Windows
                status = self.connection.status()
                
                if status != obd.OBDStatus.NOT_CONNECTED:  # Check if connected
                    print(f"Connection successful! Status: {status}")
                    break  # Exit the loop once connected
                else:
                    print(f"Connection status: {status}, retrying...")
            except Exception as e:
                print(f"Error connecting: {e}, retrying...")
            time.sleep(2)  # Wait for 2 seconds before retrying

    def addValue(self, name: str, querryReference):
        self.names.append(name)
        self.querryReferences.append(querryReference)
        self.querryOutput.append(None)

    def convert_to_standard_units(self, index, value):
        # Convert the sensor value into standard units
        if self.names[index] == "Speed":
            # Convert speed from km/h to mph
            return int(value * 0.621371)
        elif self.names[index] == "Intake_Temp" or self.names[index] == "Ambiant_Air_Temp" or self.names[index] == "Coolant_temp":
            # Convert temperature from Celsius to Fahrenheit
            return int(value * 9 / 5 + 32)
        elif self.names[index] == "MAF":
            # Convert Mass Air Flow from g/s to lbs/min
            return int(value * 0.00220462)
        else:
            # No conversion needed for RPM, Engine Load, etc.
            return int(value)

    def _getDataString(self):
        string = ""
        for i in range(len(self.querryReferences)):
            result = self.connection.query(self.querryReferences[i])
            if result.is_null():
                self.querryOutput[i] = 0  # No data received
            else:
                self.querryOutput[i] = result.value  # Extract numeric value
            # Convert to standard units
            self.querryOutput[i] = self.convert_to_standard_units(i, self.querryOutput[i])
            string += f"{self.querryOutput[i]}          "
        return string

    def getQuerryOutput(self):
        return self.querryOutput

    def displayLoop(self, app):
        data = self._getDataString()
        app.update_gauge(self.getQuerryOutput())  # Pass the real-time data for gauges

        print(data)
        app.after(100, self.displayLoop, app)


if __name__ == "__main__":
    obdPro = ObdPro()
    obdPro.addValue("Speed", obd.commands.SPEED)
    obdPro.addValue("Rpm", obd.commands.RPM)
    obdPro.addValue("Engine_Load", obd.commands.ENGINE_LOAD)
    obdPro.addValue("MAF", obd.commands.MAF)
    obdPro.addValue("Intake_Temp", obd.commands.INTAKE_TEMP)
    obdPro.addValue("Ambiant_Air_Temp", obd.commands.AMBIANT_AIR_TEMP)
    obdPro.addValue("Coolant_temp", obd.commands.COOLANT_TEMP)
    obdPro.addValue("Spark_adv", obd.commands.TIMING_ADVANCE)

    # Define realistic ranges for each sensor
    ranges = [
        #start,stop, green, red
        (0, 135, 0, 135),           # Speed (mph) - converted from 0-200 km/h
        (0, 7500, 2000, 5000),      # RPM
        (0, 100, 0, 80),            # Engine Load (%)
        (0, 100, 0, 100),           # MAF (lbs/min)
        (20, 120, 20, 80),          # Intake Temperature (°F)
        (-4, 122, -4, 122),         # Ambient Air Temperature (°F)
        (100, 250, 190, 230),         # Coolant Temperature (°F)
        (0, 50, 0, 50),             # Spark Advance (degrees)
    ]
    units = [
        "mph",         # Speed
        "RPM",         # RPM
        "%",           # Engine Load
        "lbs/min",     # MAF
        "°F",          # Intake Temperature
        "°F",          # Ambient Air Temperature
        "°F",          # Coolant Temperature
        "degrees",     # Spark Advance
    ]
    
    # Create a CarDashboard with the names, initial values, ranges, and units
    app = CarDashboard(obdPro.names, obdPro.getQuerryOutput(), ranges, units)

    # Start the display loop to continuously fetch and display data
    obdPro.displayLoop(app)

    # Start Tkinter event loop
    app.mainloop()
