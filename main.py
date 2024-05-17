import tkinter as tk
from tkinter import ttk
from threading import Thread, Timer
from pynput.keyboard import Key, Controller
import serial.tools.list_ports
import serial
import time

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

        self.port_labels = []
        self.port_comboboxes = []
        self.connect_buttons = []
        self.disconnect_buttons = []
        self.received_data_labels = []
        self.serial_communications = []

        self.last_key_press_timers = {i: None for i in range(4)}
        self.last_key_press_data = {i: None for i in range(4)}
        self.received_data_dict = {i: tk.StringVar() for i in range(4)}

        for i in range(4):
            port_label = ttk.Label(root, text=f"Select Port {i+1}:")
            port_combobox = ttk.Combobox(root, values=self.get_available_ports())
            connect_button = ttk.Button(root, text=f"Connect {i+1}", command=lambda i=i: self.connect(i))
            disconnect_button = ttk.Button(root, text=f"Disconnect {i+1}", command=lambda i=i: self.disconnect(i))
            received_data_label = ttk.Label(root, text=f"Received Data {i+1}:")

            row = i * 2
            col = 0

            port_label.grid(row=row, column=col, sticky="w", padx=5, pady=5)
            port_combobox.grid(row=row, column=col+1, sticky="ew", padx=5, pady=5)
            connect_button.grid(row=row, column=col+2, sticky="ew", padx=5, pady=5)
            disconnect_button.grid(row=row, column=col+3, sticky="ew", padx=5, pady=5)
            received_data_label.grid(row=row+1, column=col, columnspan=4, sticky="ew", padx=5, pady=5)

            self.port_labels.append(port_label)
            self.port_comboboxes.append(port_combobox)
            self.connect_buttons.append(connect_button)
            self.disconnect_buttons.append(disconnect_button)
            self.received_data_labels.append(received_data_label)
            self.serial_communications.append(None)

        self.refresh_button = ttk.Button(root, text="Refresh Ports", command=self.update_available_ports)
        self.refresh_button.grid(row=8, column=0, columnspan=4, pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.disconnect_and_exit)

        self.keyboard_controllers = [Controller() for _ in range(4)]
        self.start_received_data_thread()

    def get_available_ports(self):
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(port.name)
        return ports

    def update_available_ports(self):
        ports = self.get_available_ports()
        for i in range(4):
            self.port_comboboxes[i]["values"] = ports

    def connect(self, index):
        selected_port = self.port_comboboxes[index].get()
        if not selected_port:
            return

        baudrate = 115200
        self.serial_communications[index] = SerialCommunication(selected_port, baudrate, lambda data, i=index: self.update_received_data(data, i))

        if self.serial_communications[index].open_connection():
            print(f"Connected to {selected_port}")
            self.serial_communications[index].start()

    def disconnect(self, index):
        if self.serial_communications[index]:
            self.serial_communications[index].stop()
            self.serial_communications[index].close_connection()
            print(f"Disconnected from Port {index+1}")

    def disconnect_and_exit(self):
        for i in range(4):
            self.disconnect(i)
        self.root.destroy()

    def update_received_data(self, data, index):
        self.received_data_dict[index].set(data)
        self.handle_key_press(index, data)

    def start_received_data_thread(self):
        self.root.after(100, self.update_received_data_thread)

    def update_received_data_thread(self):
        for i in range(4):
            self.received_data_labels[i].config(text=f"Received Data {i+1}: {self.received_data_dict[i].get()}")

        self.root.after(100, self.update_received_data_thread)

    def handle_key_press(self, index, data):
        if self.last_key_press_timers[index] is not None and self.last_key_press_timers[index].is_alive():
            if data == self.last_key_press_data[index]:
                self.last_key_press_timers[index].cancel()
            else:
                self.last_key_press_timers[index] = None
                self.release_all_keys(index)

        if data.lower() == "stp":
            self.release_all_keys(index)
            self.last_key_press_timers[index] = None
            self.last_key_press_data[index] = None
        else:
            if data.lower() == "up":
                self.keyboard_controllers[index].press(Key.up)
            elif data.lower() == "down":
                self.keyboard_controllers[index].press(Key.down)
            elif data.lower() == "esc":
                self.keyboard_controllers[index].press(Key.esc)
            elif data.lower() == "right":
                self.keyboard_controllers[index].press(Key.right)
            elif data.lower() == "left":
                self.keyboard_controllers[index].press(Key.left)
            elif len(data) == 1:
                self.keyboard_controllers[index].press(data)

            self.last_key_press_data[index] = data
            self.last_key_press_timers[index] = Timer(1, lambda i=index: self.release_all_keys(i))
            self.last_key_press_timers[index].start()

    def release_all_keys(self, index):
        # Release all keys individually
        self.keyboard_controllers[index].release(Key.up)
        self.keyboard_controllers[index].release(Key.down)
        self.keyboard_controllers[index].release(Key.esc)
        self.keyboard_controllers[index].release(Key.right)
        self.keyboard_controllers[index].release(Key.left)

        # Release alphabet keys based on the last received data
        last_data = self.last_key_press_data[index]
        if last_data and len(last_data) == 1 and last_data.isalpha():
            self.keyboard_controllers[index].release(last_data)

        # Release any other keys you may want to handle

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
