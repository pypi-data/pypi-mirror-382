import socket
import threading
import json
import struct
import tkinter as tk
import cv2
import numpy as np
import time
from .utils import setup_logging, enforce_type
from tkinter import scrolledtext

class ParagraphScreenShareClient:
    FORMAT = "utf-8"
    DISCONNECT_MSG = "DISCONNECT"
    PLACEHOLDER = "Enter IPV4 to connect:"

    def __init__(self, default_ip=None, port : int = 5050):
        enforce_type(default_ip, (str, type(None)), "default_ip")
        enforce_type(port, int, "port")
        self.HOST = default_ip or ""
        self.PORT = port
        self.client = None
        self.connecting = False
        self.latest_frame = None
        self.OUTPUT = ""

        # GUI attributes
        self.root = None
        self.ip_entry = None
        self.input_entry = None
        self.output_var = None

        self.logger = setup_logging(self.__class__.__name__)

    # ------------------- Networking Logic -------------------

    def receive_image(self):
        """Continuously receive image frames from the server."""
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
                if self.output_var is not None: self.output_var.set(self.OUTPUT)
                self.connecting = False
                break

    def start_client(self):
        """Attempt to connect to the host and start receiving frames."""
        try:
            self.logger.info(f"Trying to connect to {self.HOST}:{self.PORT}")
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.HOST, self.PORT))
            self.connecting = True
            self.OUTPUT = f"Connected to {self.HOST}:{self.PORT}"
            if self.output_var is not None: self.output_var.set(self.OUTPUT)
        except socket.error as e:
            self.OUTPUT = f"Error connecting to {self.HOST}:{self.PORT}: {e}"
            if self.output_var is not None: self.output_var.set(self.OUTPUT)
            self.connecting = False
            return

        threading.Thread(target=self.receive_image, daemon=True).start()

        # Show frames while connected
        while self.connecting:
            if self.latest_frame is not None:
                cv2.imshow("Host Screen", self.latest_frame)
                if cv2.waitKey(1) & 0xFF == 27:  # ESC key in OpenCV window
                    self.exit()
                    break
            else:
                time.sleep(0.01)

        cv2.destroyAllWindows()
        
    def exit(self):
        """Disconnect from the host."""
        if not self.connecting:
            self.logger.info("No connection to disconnect")
            return
        
        self.logger.info("[EXIT] Disconnecting...")
        if self.connecting and self.client:
            try:
                self.client.sendall(self.DISCONNECT_MSG.encode(self.FORMAT))
            except Exception as e:
                if self.output_var is not None: self.output_var.set(f"[ERROR in exit] {e}")
        self.connecting = False
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass
        if self.output_var is not None: self.output_var.set("Disconnected from host.")
        self.logger.info("Client disconnected.")

    # ------------------- GUI -------------------

    def on_connect(self):
        """Triggered when the 'Connect' button is pressed."""
        ip_value = self.ip_entry.get().strip() 
        if not ip_value or ip_value == self.PLACEHOLDER:
            if self.output_var is not None: self.output_var.set("Please enter a valid IP address.")
            return

        self.HOST = ip_value
        if self.output_var is not None: self.output_var.set("Connecting...")
        threading.Thread(target=self.start_client, daemon=True).start()

    def clear_placeholder(self, event):
        if self.ip_entry.get() == self.PLACEHOLDER:
            self.ip_entry.delete(0, tk.END)
            self.ip_entry.config(fg="black")

    def restore_placeholder(self, event=None):
        if not self.ip_entry.get():
            self.ip_entry.insert(0, self.PLACEHOLDER)
            self.ip_entry.config(fg='gray')

    def send_input(self):
        if not self.connecting or not self.client:
            if self.output_var is not None: self.output_var.set("Not connected to any host.")
            return

        text = self.input_entry.get("1.0", tk.END).strip() if self.input_entry is not None else "Default input"
        
        if not text:
            if self.output_var is not None: self.output_var.set("Please enter something to send.")
            return

        message = {"type": "text", "data": text}
        try:
            message_str = json.dumps(message)
            header = struct.pack(">L", len(message_str))
            self.client.sendall(header + message_str.encode(self.FORMAT))
            if self.output_var is not None: self.output_var.set(f"Sent ({len(text)} chars)")
        except Exception as e:
            if self.output_var is not None: self.output_var.set(f"[ERROR in send_input] {e}")

    def run(self):
        """Initialize the GUI with resizable multi-line input."""
        self.root = tk.Tk()
        self.root.title("Paragraph UI Client")
        self.root.geometry("600x400")  # bigger default
        self.root.minsize(400, 300)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=0)
        self.root.columnconfigure(0, weight=1)

        # Frame for IP and connection controls
        top_frame = tk.Frame(self.root)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        top_frame.columnconfigure(1, weight=1)

        self.ip_entry = tk.Entry(top_frame)
        self.ip_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        if self.HOST:
            self.ip_entry.insert(0, self.HOST)
        else:
            self.restore_placeholder()
        self.ip_entry.bind("<FocusIn>", self.clear_placeholder)
        self.ip_entry.bind("<FocusOut>", self.restore_placeholder)

        connect_button = tk.Button(top_frame, text="Connect", command=self.on_connect)
        connect_button.grid(row=0, column=1, sticky="e")

        # Middle frame: multi-line input
        mid_frame = tk.Frame(self.root)
        mid_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        mid_frame.rowconfigure(0, weight=1)
        mid_frame.columnconfigure(0, weight=1)

        tk.Label(mid_frame, text="Write your message below:").grid(row=0, column=0, sticky="w")
        self.input_entry = scrolledtext.ScrolledText(mid_frame, wrap=tk.WORD, font=("Consolas", 11))
        self.input_entry.grid(row=1, column=0, sticky="nsew", pady=(2, 5))

        # Bottom frame: output + control buttons
        bottom_frame = tk.Frame(self.root)
        bottom_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=0)
        bottom_frame.columnconfigure(2, weight=0)

        self.output_var = tk.StringVar()
        output_entry = tk.Entry(bottom_frame, textvariable=self.output_var, state="readonly")
        output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        send_button = tk.Button(bottom_frame, text="Send", command=self.send_input)
        send_button.grid(row=0, column=1, padx=(0, 5))

        stop_button = tk.Button(bottom_frame, text="Disconnect", command=self.exit)
        stop_button.grid(row=0, column=2)

        self.root.mainloop()