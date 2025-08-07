import tkinter as tk
import math

class GaugeV2(tk.Canvas):
    def __init__(
        self,
        parent,
        width: int = 240,
        height: int = 240,
        min_value=0.0,
        max_value=100.0,
        label="",
        unit="",
        major_tick_interval=5,
        divisions=20,
        yellow=60, 
        red=80,
        light_blue=40,
        blue=20,
        bg="lightgrey",
        bg_color="white",
        scale_factor=1.0,
        **kwargs
        ):
        """
        Initializes the BoostGauge canvas.
    
        Args:
            parent: The parent widget (e.g., a Tk or Frame instance).
            min_value (int): The minimum PSI value on the gauge.
            max_value (int): The maximum PSI value on the gauge.
            major_tick_interval (int): The interval between major tick marks.
            **kwargs: Additional keyword arguments for the Canvas.
        """
        super().__init__(parent, **kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.major_tick_interval = (self.max_value-self.min_value)/5
        self._label = label
        self.scale_factor = scale_factor

        # Define canvas dimensions and center. winfo_reqwidth() requires the widget to be packed first,
        # so we'll use the provided kwargs if available, or fall back to a default.
        self.width = width * self.scale_factor
        self.height = height * self.scale_factor
        self.center_x = self.width / 2
        self.center_y = self.height / 2

        # Define gauge properties
        self.radius = min(self.center_x, self.center_y) * 0.8
        self.start_angle = 210  # Gauge starts at 210 degrees (bottom-left)
        self.end_angle = -30    # Gauge ends at -30 degrees (top-right)

        # Draw the static elements of the gauge
        self.draw_gauge_elements()

        # Initialize the needle. It will be drawn at the initial PSI value.
        self.needle_id = None
        self.update_value(self.min_value)

    def draw_gauge_elements(self):
        """
        Draws the static components of the gauge, including the rings,
        tick marks, and text labels.
        """
        # Clear the canvas to redraw elements
        self.delete("all")
        
        # Outer ring
        self.create_oval(self.center_x - self.radius * 1.05, self.center_y - self.radius * 1.05,
                         self.center_x + self.radius * 1.05, self.center_y + self.radius * 1.05,
                         outline="black", width=5)

        # Inner black background circle
        self.create_oval(self.center_x - self.radius, self.center_y - self.radius,
                         self.center_x + self.radius, self.center_y + self.radius,
                         fill="black", outline="black")
        
        # Draw the center point for the needle
        self.create_oval(self.center_x - 10, self.center_y - 10,
                         self.center_x + 10, self.center_y + 10,
                         fill="black", outline="white", width=2)
        
        # Draw the BOOST label at the bottom center
        self.create_text(self.center_x, self.center_y + self.radius * 0.7,
                         text=self._label, fill="white", font=("Arial", 16, "bold"))
        
        # Draw the PSI label
        self.create_text(self.center_x + self.radius * 0.6, self.center_y + self.radius * 0.1,
                         text="PSI", fill="white", font=("Arial", 12))

        # Dynamically calculate the number of major and minor ticks
        psi_range = self.max_value - self.min_value
        num_major_ticks = int(psi_range / self.major_tick_interval)
        
        # We'll use 5 minor ticks per major tick interval for a nice visual balance.
        minor_ticks_per_major = 5
        num_all_ticks = num_major_ticks * minor_ticks_per_major
        
        # Loop to draw all tick marks and labels
        for i in range(num_all_ticks + 1):
            angle = self.start_angle + (self.end_angle - self.start_angle) * (i / num_all_ticks)
            angle_rad = math.radians(angle)
            
            # Check if this is a major tick
            is_major = (i % minor_ticks_per_major == 0)

            # Tick mark length
            tick_length = self.radius * 0.05
            if is_major:
                tick_length = self.radius * 0.1
            
            # Start and end points of the tick mark
            x1 = self.center_x + (self.radius - tick_length) * math.cos(angle_rad)
            y1 = self.center_y - (self.radius - tick_length) * math.sin(angle_rad)
            x2 = self.center_x + self.radius * math.cos(angle_rad)
            y2 = self.center_y - self.radius * math.sin(angle_rad)
            
            self.create_line(x1, y1, x2, y2, fill="white", width=2 if is_major else 1)
            
            # Draw the major tick labels
            if is_major:
                psi_value = self.min_value + (i / num_all_ticks) * psi_range
                
                label_x = self.center_x + (self.radius - tick_length * 2) * math.cos(angle_rad)
                label_y = self.center_y - (self.radius - tick_length * 2) * math.sin(angle_rad)
                
                self.create_text(label_x, label_y, text=str(int(psi_value)),
                                 fill="white", font=("Arial", 12))
    def set_theme(self, theme):
        pass
    def resetMinMax():
        pass
    def set_value(self, value):
        self.update_value(value)
    
    def update_value(self, input_value):
        # Clamp the input_value value to the valid range
        input_value = max(self.min_value, min(self.max_value, input_value))

        # Calculate the angle for the given input_value value
        input_value_range = self.max_value - self.min_value
        input_value_normalized = (input_value - self.min_value) / input_value_range
        angle = self.start_angle + input_value_normalized * (self.end_angle - self.start_angle)
        
        angle_rad = math.radians(angle)

        # Calculate needle tip position
        needle_len = self.radius * 0.9
        tip_x = self.center_x + needle_len * math.cos(angle_rad)
        tip_y = self.center_y - needle_len * math.sin(angle_rad)
        
        # Calculate base points for the needle to make it a triangle
        base_angle_rad_1 = math.radians(angle + 90)
        base_width = 10
        base_x1 = self.center_x + base_width * math.cos(base_angle_rad_1)
        base_y1 = self.center_y - base_width * math.sin(base_angle_rad_1)

        base_angle_rad_2 = math.radians(angle - 90)
        base_x2 = self.center_x + base_width * math.cos(base_angle_rad_2)
        base_y2 = self.center_y - base_width * math.sin(base_angle_rad_2)
        
        # Delete the old needle if it exists
        if self.needle_id:
            self.delete(self.needle_id)
        
        # Create a new needle polygon
        self.needle_id = self.create_polygon(tip_x, tip_y, base_x1, base_y1, base_x2, base_y2,
                                             fill="red", outline="red", width=2)
        
# --- Example Usage ---
def create_gauge_and_slider(root, min_value, max_value, major_interval, label=""):
    """
    Helper function to create a BoostGauge and a corresponding slider.
    """
    gauge = GaugeV2(root, min_value=min_value, max_value=max_value, major_tick_interval=major_interval, label=label, bg="white")
    gauge.pack(padx=20, pady=20)

    def on_slider_move(value):
        try:
            input_value = float(value)
            gauge.update_value(input_value)
        except ValueError:
            pass

    slider = tk.Scale(
        root,
        from_=min_value,
        to=max_value,
        orient="horizontal",
        label=f"Set PSI (Range: {min_value} to {max_value})",
        length=300,
        resolution=1, # Set resolution to 1 to match the tick interval
        command=on_slider_move
    )
    slider.set(min_value) # Set initial value
    slider.pack(pady=10)
    
    return gauge, slider

if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()
    root.title("Adjustable Boost Gauge")
    
    # Example 1: Original gauge setup
    create_gauge_and_slider(root, min_value=-20, max_value=30, major_interval=10)

    # Example 2: A different range with a different major tick interval
    root_2 = tk.Toplevel(root)
    root_2.title("Custom Boost Gauge")
    create_gauge_and_slider(root_2, min_value=-30, max_value=300, major_interval=50, label="BOOST")

    # Start the Tkinter event loop
    root.mainloop()
