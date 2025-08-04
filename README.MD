### OBD Pro: A Customizable Car Dashboard

ObdPro is a Python-based application that is meant to run on a rasberry pi to turn it into a real-time car dashboard. It connects to your car's On-Board Diagnostics II (OBD-II) port via an adapter and displays live data from the vehicle's sensors on a customizable interface. This app is designed for car enthusiasts, hobbyists, or anyone who wants a better view of their vehicle's performance.

-----

### Features

  * **Real-Time Gauges**: Displays up to four live data feeds from your car's sensors simultaneously on a clean, easy-to-read dashboard.
  * **Customizable Gauges**: You can select which parameters (e.g., RPM, speed, engine load) you want to display on each of the four gauges via the settings menu.
  * **Debug Mode**: Don't have a car handy? The app includes a debug mode that simulates random sensor data, allowing you to test the interface without a physical connection.
  * **Theme Switching**: Easily toggle between a light and dark theme to suit your preferences or driving conditions.
  * **Fullscreen Mode**: Maximize the display for a distraction-free view with a dedicated fullscreen toggle.
  * **Lugging Warning**: Get a visual warning when your engine is running in a low RPM, high-load condition that could be harmful.
  * **Error Reporting**: The app provides a console-like output for connection status and error messages, helping you troubleshoot any issues.

-----

### How It Works

This application is built with the **[Tkinter](https://docs.python.org/3/library/tkinter.html)** library for the user interface and uses the **[python-OBD](https://python-obd.readthedocs.io/en/latest/)** library to communicate with your vehicle's OBD-II port.

1.  **Connection**: The app attempts to connect to your OBD-II adapter, which is assumed to be a Bluetooth or USB device (e.g., on `/dev/ttyUSB0` for Linux).
2.  **Data Retrieval**: It queries the car's ECU (Engine Control Unit) for various sensor data, such as RPM, speed, and temperatures.
3.  **Display**: The data is then displayed on the main screen using a custom gauge widget.

-----

### Requirements

To use this application, you will need:

  * **Python 3**: The app is written in Python and requires a Python 3 environment.
  * **`python-OBD` Library**: Install this library using pip:
    ```bash
    pip install python-obd
    ```
To use with a vehicle, you will need:

  * **OBD-II Adapter**: A physical OBD-II adapter (e.g., ELM327) that connects to your car's diagnostic port and communicates via Bluetooth or a serial port.
  * **A Vehicle**: Any modern vehicle (typically 1996 and newer in the US) with a standard OBD-II port.

-----

### Usage

1.  **Connect the Adapter**: Plug your OBD-II adapter into your car's port. Make sure it's discoverable or connected to your computer.
2.  **Run the App**: Execute the main script from your terminal:
    ```bash
    python main.py
    ```
3.  **Start the Engine**: The app will attempt to connect to your car. Once connected, the gauges will display live data.
4.  **Customize**: Use the **Settings** button to change which values are shown on the gauges, toggle themes, or switch to fullscreen mode.
