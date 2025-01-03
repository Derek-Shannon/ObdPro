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
    """

    def __init__(
        self,
        parent,
        width: int = 200,
        height: int = 100,
        min_value=0.0,
        max_value=100.0,
        label="",
        unit="",
        divisions=20,
        yellow=50,
        red=80,
        yellow_low=0,
        red_low=10,
        bg="lightgrey",
        bg_color="white"
    ):
        self._parent = parent
        self._width = width
        self._height = height
        self._label = label
        self._unit = unit
        self._divisions = divisions
        self._min_value = int(min_value)
        self._max_value = int(max_value)
        self._average_value = int((max_value + min_value) / 2)
        self._yellow = yellow * 0.01
        self._red = red * 0.01
        self._yellow_low = yellow_low * 0.01
        self._red_low = red_low * 0.01
        self.bg_color = bg_color

        super().__init__(self._parent)

        self._canvas = tk.Canvas(self, width=self._width, height=self._height, bg=bg)
        self._canvas.grid(row=0, column=0, sticky="news")
        self._min_value = int(min_value)
        self._max_value = int(max_value)
        self._value = self._min_value
        self._redraw()

    def _redraw(self):
        self._canvas.delete("all")
        max_angle = 120.0
        value_as_percent = (self._value - self._min_value) / (
            self._max_value - self._min_value
        )
        value = float(max_angle * value_as_percent)
        # no int() => accuracy
        # create the tick marks and colors across the top
        for i in range(self._divisions):
            extent = max_angle / self._divisions
            start = 150.0 - i * extent
            rate = (i + 1) / (self._divisions + 1)
            if rate < self._red_low:
                bg_color = "red"
            elif rate <= self._yellow_low:
                bg_color = "yellow"
            elif rate <= self._yellow:
                bg_color = "green"
            elif rate <= self._red:
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
            )
        bg_color = self.bg_color
        red = "#c21807"
        ratio = 0.06
        self._canvas.create_arc(
            self._width * ratio,
            int(self._height * 0.25),
            self._width * (1.0 - ratio),
            int(self._height * 1.8 * (1.0 - ratio * 1.1)),
            start=150,
            extent=-120,
            width=2,
            fill=bg_color,
            style="pie",
        )
        # readout & title
        self.readout(self._value, "black")  # BG black if OK

        # display lowest value
        value_text = "{}".format(self._min_value)
        self._canvas.create_text(
            self._width * 0.1,
            self._height * 0.7,
            font=("Courier New", 10),
            text=value_text,
        )
        # display greatest value
        value_text = "{}".format(self._max_value)
        self._canvas.create_text(
            self._width * 0.9,
            self._height * 0.7,
            font=("Courier New", 10),
            text=value_text,
        )
        # display center value
        value_text = "{}".format(self._average_value)
        self._canvas.create_text(
            self._width * 0.5,
            self._height * 0.1,
            font=("Courier New", 10),
            text=value_text,
        )
        # create first half (red needle)
        self._canvas.create_arc(
            0,
            int(self._height * 0.15),
            self._width,
            int(self._height * 1.8),
            start=150,
            extent=-value,
            width=3,
            outline=red,
        )

        # create inset red
        self._canvas.create_arc(
            self._width * 0.35,
            int(self._height * 0.75),
            self._width * 0.65,
            int(self._height * 1.2),
            start=150,
            extent=-120,
            width=1,
            outline="grey",
            fill=red,
            style="pie",
        )

        # create the overlapping border
        self._canvas.create_arc(
            0,
            int(self._height * 0.15),
            self._width,
            int(self._height * 1.8),
            start=150,
            extent=-120,
            width=4,
            outline="#343434",
        )

    def readout(self, value, bg):  # value, BG color
        # draw the black behind the readout
        r_width = 95
        r_height = 20
        r_offset = 8
        self._canvas.create_rectangle(
            self._width / 2.0 - r_width / 2.0,
            self._height / 2.0 - r_height / 2.0 + r_offset,
            self._width / 2.0 + r_width / 2.0,
            self._height / 2.0 + r_height / 2.0 + r_offset,
            fill=bg,
            outline="grey",
        )
        # the digital readout
        self._canvas.create_text(
            self._width * 0.5,
            self._height * 0.5 - r_offset,
            font=("Courier New", 10),
            text=self._label,
        )

        value_text = "{}{}".format(self._value, self._unit)
        self._canvas.create_text(
            self._width * 0.5,
            self._height * 0.5 + r_offset,
            font=("Courier New", 10),
            text=value_text,
            fill="white",
        )

    def set_value(self, value):
        self._value = int(value)
        if self._min_value * 1.02 < value < self._max_value * 0.98:
            self._redraw()  # refresh all
        else:  # OFF limits refresh only readout
            self.readout(self._value, "red")  # on RED BackGround
    def update_gauge_randomly(self, gauge):
        # Generate a random value within the gauge's range
        random_value = random.uniform(gauge._min_value, gauge._max_value)
        gauge.set_value(random_value)
        # Schedule the next update
        gauge.after(500, self.update_gauge_randomly, gauge)  # Update every 500ms



# if __name__ == "__main__":
#     root = tk.Tk()
#     root.title("Gauge with Random Values")

#     # Create a gauge instance
#     gauge = Gauge(root, max_value=120.0, label="Speed", unit="km/h", yellow=30, red=70)
#     gauge.grid(padx=20, pady=20)

#     # Start the random value updates
#     gauge.update_gauge_randomly(gauge)

#     root.mainloop()
