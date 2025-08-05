import random
import tkinter as tk

class Gauge(tk.Frame):
    """
    Shows a gauge, much like the RotaryGauge.::

        gauge = tk_tools.Gauge(root, max_value=100.0,
                               label='speed', unit='km/h')
        gauge.grid()
        gauge.set_value(10)

    :param parent: tkinter parent frame
    :param width: canvas width
    :param height: canvas height
    :param min_value: the minimum value
    :param max_value: the maximum value
    :param label: the label on the scale
    :param unit: the unit to show on the scale
    :param divisions: the number of divisions on the scale
    :param yellow: the beginning of the yellow (warning) zone in percent
    :param red: the beginning of the red (danger) zone in percent
    :param yellow_low: in percent warning for low values
    :param red_low: in percent if very low values are a danger
    :param bg: background
    :param bg_color: background color for the inner part of the gauge
    """

    def __init__(
        self,
        parent,
        width: int = 190,
        height: int = 100,
        min_value=0.0,
        max_value=100.0,
        label="",
        unit="",
        divisions=20,
        yellow=60, 
        red=80,
        light_blue=40,
        blue=20,
        bg="lightgrey",
        bg_color="white",
        scale_factor=1.0
    ):
        self._parent = parent
        self._scale_factor = scale_factor
        self._width = width * self._scale_factor
        self._height = height * self._scale_factor
        self._label = label
        self._unit = unit
        self._divisions = divisions
        self._min_value = int(min_value)
        self._max_value = int(max_value)
        self._average_value = int((max_value + min_value) / 2)
        self._yellow = yellow
        self._red = red
        self._light_blue = light_blue
        self._blue = blue
        

        # Theme colors will be managed here
        self.theme_colors = {
            'light': {
                'frame_bg': 'lightgrey',
                'canvas_bg': 'lightgrey',
                'inner_bg': 'white',
                'text': 'black',
                'outline': '#343434'
            },
            'dark': {
                'frame_bg': '#2C2C2C',
                'canvas_bg': '#2C2C2C',
                'inner_bg': '#1E1E1E',
                'text': '#F0F0F0',
                'outline': '#FFFFFF'
            }
        }
        self.current_theme = 'light'
        super().__init__(self._parent)

        self._canvas = tk.Canvas(self, width=self._width, height=self._height, bg=self.theme_colors[self.current_theme]['canvas_bg'], highlightthickness=0)
        self._canvas.pack()

        self._min_value = int(min_value)
        self._max_value = int(max_value)
        self._value = self._min_value
        
        # min/max value display
        container = tk.Frame(self, bg=self.theme_colors[self.current_theme]['frame_bg'])
        container.pack()
        self.variableMax = self._value
        self.variableMin = self._value
        self.max_value_label = tk.Label(container, text=f"to {self.variableMax}{self._unit}", bg=self.theme_colors[self.current_theme]['frame_bg'], fg=self.theme_colors[self.current_theme]['text'], font=("Courier New", int(10*self._scale_factor)))
        self.max_value_label.grid(column=1, row=0, sticky="e")
        self.min_value_label = tk.Label(container, text=f"{self.variableMin}{self._unit}", bg=self.theme_colors[self.current_theme]['frame_bg'], fg=self.theme_colors[self.current_theme]['text'], font=("Courier New", int(10*self._scale_factor)))
        self.min_value_label.grid(column=0, row=0, sticky="w")
        
        self.configure(bg=self.theme_colors[self.current_theme]['frame_bg'])
        self._redraw()

    def set_theme(self, theme):
        """Sets the theme of the gauge and redraws it."""
        self.current_theme = theme
        self.configure(bg=self.theme_colors[self.current_theme]['frame_bg'])
        self._canvas.config(bg=self.theme_colors[self.current_theme]['canvas_bg'])
        
        # Update label colors
        self.max_value_label.config(bg=self.theme_colors[self.current_theme]['frame_bg'], fg=self.theme_colors[self.current_theme]['text'])
        self.min_value_label.config(bg=self.theme_colors[self.current_theme]['frame_bg'], fg=self.theme_colors[self.current_theme]['text'])

        # Update the container's background color
        self.max_value_label.master.config(bg=self.theme_colors[self.current_theme]['frame_bg'])
        self.min_value_label.master.config(bg=self.theme_colors[self.current_theme]['frame_bg'])

        self._redraw()

    def _redraw(self):
        self._canvas.delete("all")
        max_angle = 120.0
        value_as_percent = (self._value - self._min_value) / (
            self._max_value - self._min_value
        )
        value = float(max_angle * value_as_percent)
        
        for i in range(self._divisions):
            extent = max_angle / self._divisions
            start = 150.0 - i * extent
            value_at_division = self._min_value + (self._max_value - self._min_value) * (i / self._divisions)
            
            if value_at_division < self._blue:
                bg_color = "blue"
            elif value_at_division < self._light_blue:
                bg_color = "lightblue"
            elif value_at_division < self._yellow:
                bg_color = "green"
            elif value_at_division < self._red:
                bg_color = "yellow"
            else:
                bg_color = "red"

            self._canvas.create_arc(
                0,
                int(self._height * 0.15),
                self._width,
                int(self._height * 1.8),
                start=start,
                extent=-extent,
                width=2,
                fill=bg_color,
                style="pie",
                outline=bg_color # Added outline to match fill for a solid look
            )
            
        # Draw the inner background arc
        inner_bg_color = self.theme_colors[self.current_theme]['inner_bg']
        ratio = 0.06
        self._canvas.create_arc(
            self._width * ratio,
            int(self._height * 0.25),
            self._width * (1.0 - ratio),
            int(self._height * 1.8 * (1.0 - ratio * 1.1)),
            start=150,
            extent=-120,
            width=2,
            fill=inner_bg_color,
            style="pie",
            outline=inner_bg_color # Added outline to match fill
        )
        
        # readout & title
        if self._value < self._blue:
            self.readout(self._value, "blue")
        elif self._value < self._light_blue:
            self.readout(self._value, "lightblue")
        elif self._value < self._yellow:
            self.readout(self._value, "green")
        elif self._value < self._red:
            self.readout(self._value, "yellow")
        else:
            self.readout(self._value, "red")
        
        # min/max
        self.max_value_label.config(text=f"to {self.variableMax}{self._unit}\n\n\n")
        self.min_value_label.config(text=f"{self.variableMin}{self._unit}\n\n\n")

        text_color = self.theme_colors[self.current_theme]['text']

        # display lowest value
        value_text = "{}".format(self._min_value)
        self._canvas.create_text(
            self._width * 0.1,
            self._height * 0.7,
            font=("Courier New", int(10*self._scale_factor)),
            text=value_text,
            fill=text_color,
        )
        # display greatest value
        value_text = "{}".format(self._max_value)
        self._canvas.create_text(
            self._width * 0.9,
            self._height * 0.7,
            font=("Courier New", int(10*self._scale_factor)),
            text=value_text,
            fill=text_color,
        )
        # display center value
        value_text = "{}".format(self._average_value)
        self._canvas.create_text(
            self._width * 0.5,
            self._height * 0.1,
            font=("Courier New", int(10*self._scale_factor)),
            text=value_text,
            fill=text_color,
        )
        # create first half (red needle)
        red_needle = "#c21807"
        self._canvas.create_arc(
            0,
            int(self._height * 0.15),
            self._width,
            int(self._height * 1.8),
            start=150,
            extent=-value,
            width=3,
            outline=red_needle,
        )

        # create inset red
        red_inset = "#c21807"
        self._canvas.create_arc(
            self._width * 0.35,
            int(self._height * 0.75),
            self._width * 0.65,
            int(self._height * 1.2),
            start=150,
            extent=-120,
            width=1,
            outline="grey",
            fill=red_inset,
            style="pie",
        )

        # create the overlapping border
        outline_color = self.theme_colors[self.current_theme]['outline']
        self._canvas.create_arc(
            0,
            int(self._height * 0.15),
            self._width,
            int(self._height * 1.8),
            start=150,
            extent=-120,
            width=4,
            outline=outline_color,
        )

    def readout(self, value, bg):
        # draw the black behind the readout
        r_width = 95*self._scale_factor
        r_height = 20*self._scale_factor
        r_offset = 8*self._scale_factor
        self._canvas.create_rectangle(
            self._width / 2.0 - r_width / 2.0,
            self._height / 2.0 - r_height / 2.0 + r_offset,
            self._width / 2.0 + r_width / 2.0,
            self._height / 2.0 + r_height / 2.0 + r_offset,
            fill=bg,
            outline="grey",
        )
        # the digital readout
        text_color = self.theme_colors[self.current_theme]['text']
        self._canvas.create_text(
            self._width * 0.5,
            self._height * 0.5 - r_offset,
            font=("Courier New", int(10*self._scale_factor)),
            text=self._label,
            fill=text_color,
        )

        value_text = "{}{}".format(self._value, self._unit)
        if bg in ["yellow", "lightblue", "red"]:
            self._canvas.create_text(
                self._width * 0.5,
                self._height * 0.5 + r_offset,
                font=("Courier New", int(10*self._scale_factor)),
                text=value_text,
                fill="black",
            )
        else:
            self._canvas.create_text(
                self._width * 0.5,
                self._height * 0.5 + r_offset,
                font=("Courier New", int(10*self._scale_factor)),
                text=value_text,
                fill="white",
            )
            
    def resetMinMax(self):
        self.variableMax = self._value
        self.variableMin = self._value
        
    def set_value(self, value):
        self._value = int(value)
        # update min/max
        if self._value > self.variableMax:
            self.variableMax = self._value
        elif self._value < self.variableMin:
            self.variableMin = self._value
        self._redraw()
        
    def update_gauge_randomly(self, gauge):
        # Generate a random value within the gauge's range
        random_value = random.uniform(gauge._min_value, gauge._max_value)
        gauge.set_value(random_value)
        # Schedule the next update
        gauge.after(500, self.update_gauge_randomly, gauge)

# Main application logic
def toggle_theme():
    """Toggles the dark/light theme for the application."""
    current_theme = gauge.current_theme
    new_theme = 'dark' if current_theme == 'light' else 'light'
    
    root_bg_color = gauge.theme_colors[new_theme]['frame_bg']
    root.configure(bg=root_bg_color)
    gauge.set_theme(new_theme)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Gauge with Random Values & Theme Toggle")
    root.geometry("240x250") # Added a fixed size to prevent widget resizing issues

    # Create a gauge instance
    gauge = Gauge(root, max_value=120.0, label="Speed", unit="km/h")
    gauge.grid(padx=20, pady=20)
    
    # Create the dark/light theme button
    theme_button = tk.Button(root, text="Toggle Dark/Light Theme", command=toggle_theme)
    theme_button.grid(padx=20, pady=10)

    # Start the random value updates
    gauge.update_gauge_randomly(gauge)

    root.mainloop()
