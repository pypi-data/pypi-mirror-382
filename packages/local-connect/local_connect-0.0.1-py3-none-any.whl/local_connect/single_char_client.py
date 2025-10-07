import socket
import struct
import cv2
import time
import threading
import keyboard
import json
import numpy as np
from .utils import time_it, setup_logging, enforce_type
import tkinter as tk

class SingleCharScreenShareClient:
    AMOUNT_OF_BYTE_PER = 4096
    PORT = 5050
    FORMAT = "utf-8"
    DISCONNECT_MSG = "DISCONNECT"

    def __init__(self, default_ip: str):
        enforce_type(default_ip, str, "default_ip")
        self.HOST = default_ip
        self.client = None
        self.connecting = False
        self.allow_input = True
        self.latest_frame = None
        self.logger = setup_logging(self.__class__.__name__)
        self.hotkey_handles = []

    # ------------------ Control ------------------
    def toggle_input(self):
        self.allow_input = not self.allow_input
        self.logger.info(f"Allow input is now: {self.allow_input}")

    def exit(self):
        self.logger.info("[EXIT] 'Esc' pressed.")
        if self.client:
            payload = self.DISCONNECT_MSG.encode(self.FORMAT)
            header = struct.pack(">L", len(payload))
            try:
                self.client.sendall(header + payload)
                self.client.shutdown(socket.SHUT_RDWR)
            except Exception as e:
                self.logger.error(f"[WARN] during shutdown send: {e}")
            finally:
                self.client.close()
                self.client = None
        self.connecting = False
        
        for handle in self.hotkey_handles:
            keyboard.remove_hotkey(handle)
        self.hotkey_handles.clear()
        keyboard.unhook_all()

    # ------------------ Networking ------------------
    def receive_image(self):
        payload_size = struct.calcsize(">L")
        data = b""

        while self.connecting:
            try:
                while len(data) < payload_size:
                    packet = self.client.recv(self.AMOUNT_OF_BYTE_PER)
                    if not packet:
                        self.connecting = False
                        break
                    data += packet
                if not data:
                    break

                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack(">L", packed_msg_size)[0]

                while len(data) < msg_size:
                    packet = self.client.recv(self.AMOUNT_OF_BYTE_PER)
                    if not packet:
                        self.connecting = False
                        break
                    data += packet
                if len(data) < msg_size:
                    break

                frame_data = data[:msg_size]
                data = data[msg_size:]

                frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
                self.latest_frame = frame

            except Exception as e:
                self.logger.error(f"{e}")
                self.connecting = False
                break

    @time_it
    def send_key(self, event):
        if not self.allow_input or keyboard.is_pressed("`"):
            return

        modifiers = []
        if keyboard.is_pressed("ctrl"):
            modifiers.append("ctrl")
        if keyboard.is_pressed("shift"):
            modifiers.append("shift")
        if keyboard.is_pressed("alt"):
            modifiers.append("alt")

        if modifiers and event.name not in ["ctrl", "shift", "alt"]:
            keys = modifiers + [event.name.lower() if isinstance(event.name, str) and 'A' <= event.name <= 'z' else event.name]
            message = {"type": "hotkey", "keys": keys}
        else:
            message = {"key": event.name, "event_type": "down"}

        message_str = json.dumps(message)
        header = struct.pack(">L", len(message_str))
        try:
            self.client.sendall(header + message_str.encode("utf-8"))
        except Exception as e:
            self.logger.error(f"{e}")

    # ------------------ Main ------------------
    def run(self):
        try:
            self.logger.info("Trying to connect to HOST")
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.HOST, self.PORT))
            self.connecting = True
            self.logger.info(f"Successfully connected to {self.HOST}:{self.PORT}")
        except socket.error as e:
            self.logger.error(f"Error connecting to {self.HOST}:{self.PORT}: {e}")
            self.connecting = False
            return

        image_thread = threading.Thread(target=self.receive_image, daemon=True)
        image_thread.start()

        self.hotkey_handles.append(keyboard.add_hotkey("`", self.toggle_input))
        self.hotkey_handles.append(keyboard.add_hotkey("esc", self.exit))
        keyboard.on_press(self.send_key)

        while self.connecting:
            if self.latest_frame is not None:
                cv2.imshow("Host Screen", self.latest_frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    try:
                        self.client.sendall(self.DISCONNECT_MSG.encode(self.FORMAT))
                    except Exception as e:
                        self.logger.error(f"{e}")
                    break
            else:
                time.sleep(0.01)

        cv2.destroyAllWindows()

        try:
            self.client.close()
        except Exception:
            pass
        self.logger.info("Disconnected from host.")

class SingleCharUIClient:
    PORT = 5050
    FORMAT = "utf-8"
    DISCONNECT_MSG = "DISCONNECT"
    PLACEHOLDER = "Enter IPV4 to connect:"

    def __init__(self, default_ip=None):
        self.HOST = default_ip or ""  # Default IP (if provided) or wait for user input
        self.client = None
        self.connecting = False
        self.allow_input = True
        self.latest_frame = None
        self.OUTPUT = ""

        # GUI attributes
        self.root = None
        self.entry = None
        self.output_var = None
        self.logger = setup_logging(self.__class__.__name__)
        self.hotkey_handles = [] 
        
    # ------------------- Logic -------------------

    def toggle_input(self):
        self.allow_input = not self.allow_input
        self.OUTPUT = f"Allow input is now: {self.allow_input}"
        self.output_var.set(self.OUTPUT)

    def receive_image(self):
        payload_size = struct.calcsize(">L")
        data = b""

        while self.connecting:
            try:
                while len(data) < payload_size:
                    packet = self.client.recv(4096)
                    if not packet:
                        self.connecting = False
                        break
                    data += packet
                if not data:
                    break

                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack(">L", packed_msg_size)[0]

                while len(data) < msg_size:
                    packet = self.client.recv(4096)
                    if not packet:
                        self.connecting = False
                        break
                    data += packet
                if len(data) < msg_size:
                    break

                frame_data = data[:msg_size]
                data = data[msg_size:]
                self.latest_frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)

            except Exception as e:
                self.OUTPUT = f"[ERROR in receive_image] {e}"
                self.output_var.set(self.OUTPUT)
                self.connecting = False
                break

    @time_it
    def send_key(self, event):
        if not self.allow_input or keyboard.is_pressed("`"):
            return
    
        modifiers = []
        if keyboard.is_pressed("ctrl"): modifiers.append("ctrl")
        if keyboard.is_pressed("shift"): modifiers.append("shift")
        if keyboard.is_pressed("alt"): modifiers.append("alt")

        if modifiers and event.name not in ["ctrl", "shift", "alt"]:
            keys = modifiers + [event.name.lower()]
            message = {"type": "hotkey", "keys": keys}
        else:
            message = {"key": event.name, "event_type": "down"}

        try:
            message_str = json.dumps(message)
            header = struct.pack(">L", len(message_str))
            self.client.sendall(header + message_str.encode("utf-8"))
        except Exception as e:
            self.OUTPUT = f"[ERROR in send_key] {e}"
            self.output_var.set(self.OUTPUT)

    def start_client(self):
        try:
            self.logger.info(f"Trying to connect to {self.HOST}:{self.PORT}")
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.HOST, self.PORT))
            self.connecting = True
            self.OUTPUT = f"Successfully connected to {self.HOST}:{self.PORT}"
            self.output_var.set(self.OUTPUT)
        except socket.error as e:
            self.OUTPUT = f"Error connecting to {self.HOST}:{self.PORT}: {e}"
            self.output_var.set(self.OUTPUT)
            self.connecting = False
            return

        threading.Thread(target=self.receive_image, daemon=True).start()

        self.hotkey_handles.append(keyboard.add_hotkey("`", self.toggle_input))
        self.hotkey_handles.append(keyboard.add_hotkey("esc", self.exit))
        keyboard.on_press(self.send_key)

        while self.connecting:
            if self.latest_frame is not None:
                cv2.imshow("Host Screen", self.latest_frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    try:
                        self.client.sendall(self.DISCONNECT_MSG.encode(self.FORMAT))
                    except Exception as e:
                        self.OUTPUT = f"[ERROR] {e}"
                    break
            else:
                time.sleep(0.01)

        cv2.destroyAllWindows()
        try:
            self.client.close()
        except Exception:
            pass
        self.logger.error("Disconnected from host.")

    # ------------------- GUI -------------------

    def on_receive(self):
        self.HOST = self.entry.get() if not self.HOST else self.HOST
        self.entry.delete(0, tk.END)
        self.output_var.set(self.OUTPUT)
        threading.Thread(target=self.start_client, daemon=True).start()

    def exit(self):
        self.logger.info("[EXIT] 'Esc' pressed. Requesting disconnect...")
        if self.connecting:
            try:
                self.client.sendall(self.DISCONNECT_MSG.encode(self.FORMAT))
            except Exception as e:
                self.OUTPUT = f"[ERROR in exit] {e}"
                self.output_var.set(self.OUTPUT)
        self.connecting = False
        for handle in self.hotkey_handles:
            keyboard.remove_hotkey(handle)
        self.hotkey_handles.clear()
        keyboard.unhook_all()
        self.output_var.set("Exit from the host")

    def clear_placeholder(self, event):
        if self.entry.get() == self.PLACEHOLDER:
            self.entry.delete(0, tk.END)
            self.entry.config(fg="black")

    def restore_placeholder(self, event=None):
        if not self.entry.get():
            self.entry.insert(0, self.PLACEHOLDER)
            self.entry.config(fg='gray')

    def run(self):
        self.root = tk.Tk()
        self.root.title("Client app")
        self.root.geometry("250x200")

        self.entry = tk.Entry(self.root)
        self.entry.pack(pady=10)
        if self.HOST:
            self.entry.insert(0, self.HOST)
        else: self.restore_placeholder()
        self.entry.bind("<FocusIn>", self.clear_placeholder)
        self.entry.bind("<FocusOut>", self.restore_placeholder)

        self.output_var = tk.StringVar()
        output_entry = tk.Entry(self.root, textvariable=self.output_var, state="readonly")
        output_entry.pack(pady=10)

        receive_button = tk.Button(self.root, text="Connect", command=self.on_receive)
        receive_button.pack(pady=5)

        stop_button = tk.Button(self.root, text="Stop connect", command=self.exit)
        stop_button.pack(pady=5)

        self.root.mainloop() #keep it exist

if __name__ == "__main__":
    app = SingleCharScreenShareClient("353")
    app.run()