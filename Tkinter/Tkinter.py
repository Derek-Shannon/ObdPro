import math
import tkinter as tk
import obd  # Make sure obd library is installed
import time, os
import random
import Gauge
import json

class CarDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Car Dashboard")
        self.geometry("850x600")

        self.gauges = []

        # Add a Reset button
        reset_button = tk.Button(self, text="Reset Max/Min", command=self.reset_values)
        reset_button.grid(column=0, row=0)
    def addGauge(self, gauge: Gauge):
        self.gauges.append(gauge)
        gauge.grid(column=len(self.gauges)-(len(self.gauges)-1)%2-1, row=len(self.gauges)%2+2)

    def get_gauge_color(self, value, min_value, max_value):
        if value < min_value:
            return "blue"
        elif value > max_value:
            return "red"
        else:
            return "green"

    def update_gauge(self, values):
        for index in range(len(self.gauges)):
            self.gauges[index].set_value(values[index])

    def reset_values(self):
        for gauge in self.gauges:
            gauge.resetMinMax()

class ObdPro:
    def __init__(self):
        self.port = "/dev/ttyUSB0"
        self.connection = None
        self.connect()

        self.names = []
        self.queryReferences = []
        self.queryOutput = [0] * 8  # Initializing with zeroes

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

    def addValue(self, name: str, queryReference):
        self.names.append(name)
        self.queryReferences.append(queryReference)

    def convert_to_standard_units(self, index, value):
        if self.names[index] == "Speed":
            return int(value * 0.621371)
        elif self.names[index] in ["Intake_Temp", "Ambiant_Temp", "Coolant_temp"]:
            return int(value * 9 / 5 + 32)
        elif self.names[index] == "MAF":
            return int(value * 0.132277)
        return int(value)

    def _getDataString(self):
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

    def displayLoop(self, app):
        self._getDataString()
        app.update_gauge(self.getQueryOutput())
        app.after(100, self.displayLoop, app)
class FakeObdPro:
    def __init__(self, data_list):
        self.data_list = data_list
        self.queryOutput = [0] * len(self.data_list)
        self.frame_counter = 0

        self.last_query_output = [0] * len(self.data_list)
        self.moveTimer = [0] * len(self.data_list)
        self.movePower = [0] * len(self.data_list)

    def generate_fake_data(self):
        new_query_output = []
        for index in range(len(data_list)):
            self.moveTimer[index] -= 1
            if self.moveTimer[index] <= 0:
                self.moveTimer[index] = random.randint(1,8)
                full_range = data_list[index].max_value-data_list[index].min_value
                self.movePower[index] = random.randint(int(-full_range/10),int(full_range/10))
            value = self.last_query_output[index]+self.movePower[index]
            new_query_output.append(max(data_list[index].min_value, min(value, data_list[index].max_value)))

        self.last_query_output = new_query_output
        self.queryOutput = new_query_output

    def getQueryOutput(self):
        self.generate_fake_data()
        return self.queryOutput

    def displayLoop(self, app):
        # Increment the frame counter
        self.frame_counter += 1

        # Check if the frame counter is a multiple of 10
        #if self.frame_counter % 3 == 0:
        app.update_gauge(self.getQueryOutput())

        # Continue the loop with a delay
        app.after(100, self.displayLoop, app)


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


if __name__ == "__main__":
    # Get the directory where the current script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, 'input_data.json')

    # Load the JSON data
    with open(json_file_path, 'r', encoding="utf-8") as file:
        json_data = json.load(file)

    # Convert JSON to Data objects
    data_list = [
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

    obdPro = None
    if True:
        obdPro = FakeObdPro(data_list)
    else:
        obdPro = ObdPro()
        for data in data_list:
            obdPro.addValue(data.name, data.query_reference)
    
    app = CarDashboard()
    #add gauges
    for data in data_list:
        app.addGauge(Gauge.Gauge(app, **data.to_gauge_params()))
    obdPro.displayLoop(app)
    app.mainloop()
