import tkinter as tk
import time
from tkinter import ttk
import serial
from threading import Thread
from pynput.keyboard import Key, Controller
import serial.tools.list_ports

class SerialCommunication(Thread):
    def __init__(self, port, baudrate, update_callback):
        Thread.__init__(self)
        self.serial_port = port
        self.baudrate = baudrate
        self.update_callback = update_callback
        self.serial = None
        self.running = False

    def open_connection(self):
        try:
            self.serial = serial.Serial(self.serial_port, self.baudrate)
            return True
        except serial.SerialException as e:
            print(f"Error: {e}")
            return False

    def close_connection(self):
        if self.serial and self.serial.is_open:
            self.serial.close()

    def run(self):
        self.running = True
        while self.running:
            if self.serial and self.serial.is_open:
                try:
                    data = self.serial.readline().decode('utf-8').strip()
                    if data:
                        self.update_callback(data)
                except serial.SerialException as e:
                    print(f"Error reading data: {e}")
                    self.close_connection()
                    self.running = False  # Stop the thread on error

    def stop(self):
        self.running = False

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Microcontroller Communication")

        self.port_label = ttk.Label(root, text="Select Port:")
        self.port_label.pack(pady=10)

        self.port_combobox = ttk.Combobox(root, values=self.get_available_ports())
        self.port_combobox.pack(pady=10)

        self.connect_button = ttk.Button(root, text="Connect", command=self.connect)
        self.connect_button.pack(pady=10)

        self.disconnect_button = ttk.Button(root, text="Disconnect", command=self.disconnect)
        self.disconnect_button.pack(pady=10)

        self.received_data_label = ttk.Label(root, text="Received Data:")
        self.received_data_label.pack(pady=10)

        self.serial_communication = None

        # Bind the window close event to the disconnect method
        self.root.protocol("WM_DELETE_WINDOW", self.disconnect_and_exit)

        # Initialize pynput keyboard controller
        self.keyboard_controller = Controller()

    def get_available_ports(self):
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(port.name)
        return ports

    def connect(self):
        selected_port = self.port_combobox.get()
        if not selected_port:
            return

        baudrate = 9600  # Modify this based on your microcontroller settings
        self.serial_communication = SerialCommunication(selected_port, baudrate, self.update_received_data)

        if self.serial_communication.open_connection():
            print(f"Connected to {selected_port}")
            self.serial_communication.start()
        else:
            print(f"Failed to connect to {selected_port}")

    def disconnect(self):
        if self.serial_communication:
            self.serial_communication.stop()
            self.serial_communication.close_connection()
            print("Disconnected")
           
    def disconnect_and_exit(self):
        # Function to call when the window is closed
        self.disconnect()
        self.root.destroy()  # Close the Tkinter window


    def update_received_data(self, data):
        # Use after() to update GUI in the main thread
        self.received_data_label.config(text=f"Received Data: {data}")

        # Simulate key presses based on received data (modify this based on your requirements)
        if(data.lower() == "up"):
           print("up")
           self.keyboard_controller.press(Key.up)
           time.sleep(0.1)
           self.keyboard_controller.release(Key.up)
        elif(data.lower() == "down"):
           self.keyboard_controller.press(Key.down)
           time.sleep(0.1)
           self.keyboard_controller.release(Key.down)
        elif(data.lower() == "right"):
           self.keyboard_controller.press(Key.right)
           time.sleep(0.1)
           self.keyboard_controller.release(Key.right)
        elif(data.lower() == "left"):
           self.keyboard_controller.press(Key.left)
           time.sleep(0.1)
           self.keyboard_controller.release(Key.left)
        else:   
            for char in data:
                if char == '\n':
                    self.keyboard_controller.press(Key.enter)
                    self.keyboard_controller.release(Key.enter)
                else:
                    self.keyboard_controller.press(char)
                    self.keyboard_controller.release(char)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()


