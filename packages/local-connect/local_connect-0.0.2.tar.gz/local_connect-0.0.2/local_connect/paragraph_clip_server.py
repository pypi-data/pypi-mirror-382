import socket
import threading
import keyboard
import time
import mss
import struct
import numpy as np
import cv2
from .utils import setup_logging, time_it, enforce_type
import pyperclip
import json
from queue import Queue

class ParagraphScreenShareServer:
    FORMAT = "utf-8"
    DISCONNECT_MSG = "DISCONNECT"

    def __init__(self, screen_width : int = 960, screen_height : int = 540, clients : int = 1, port : int = 5050):
        enforce_type(screen_height, int, "screen_height")
        enforce_type(screen_width, int, "screen_width")
        enforce_type(clients, int, "clients")
        self.max_clients = clients
        self.PORT = port
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.ADDR = (self.SERVER, self.PORT)
        self.queue = Queue()
        self.lasted_copy = ""

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(self.ADDR)

        self.server_running = True
        self.connections = []
        self.logger = setup_logging(self.__class__.__name__)
        self.screen_width = screen_width
        self.screen_height = screen_height

    # ------------------ Networking ------------------
    @time_it
    def handle_input(self, conn):
        try:
            while self.server_running:
                try:
                    header = conn.recv(4)
                except (ConnectionResetError, ConnectionAbortedError) as e:
                    self.logger.error(f" Peer closed/reset connection: {e}")
                    break

                if len(header) < 4:
                    break

                msg_length = struct.unpack(">L", header)[0]
                data = bytearray()

                while len(data) < msg_length:
                    try:
                        packet = conn.recv(msg_length - len(data))
                    except (ConnectionResetError, ConnectionAbortedError) as e:
                        self.logger.error(f" Peer aborted during recv: {e}")
                        break
                    if not packet:
                        break
                    data.extend(packet)

                if len(data) < msg_length:
                    break

                jsonfile = data.decode("utf-8")
                print(f"jsonfile {jsonfile}")
                if jsonfile == self.DISCONNECT_MSG:
                    self.logger.info(" Received graceful DISCONNECT_MSG.")
                    break
                extraction = json.loads(jsonfile)
                print(f"extraction: {extraction}")
                message = extraction.get("data")
                print(f"data : {data}")
                #add to queue and get it later (pyperclip doesnt work in thread)
                self.queue.put(message)
        finally:
            try:
                conn.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            conn.close()
            if conn in self.connections:
                self.connections.remove(conn)
            self.logger.info(" Closed input handler socket.")

    @time_it
    def stream_screen(self, conn):
        target_fps = 240
        frame_interval = 1.0 / target_fps
        last_time = time.time()

        with mss.mss() as sct:
            monitor = sct.monitors[1]
            while self.server_running:
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                frame = cv2.resize(frame, (self.screen_width, self.screen_height))

                ret, buffer = cv2.imencode(".png", frame)
                if not ret:
                    continue

                data = buffer.tobytes()
                try:
                    conn.sendall(struct.pack(">L", len(data)) + data)
                except Exception as e:
                    self.logger.error(f"Connection error: {e}")
                    break

                elapsed = time.time() - last_time
                time.sleep(max(0, frame_interval - elapsed))
                last_time = time.time()

    @time_it
    def handle_client(self, conn, addr):
        self.logger.info(f"[CONNECT TO] {addr}")
        threading.Thread(target=self.handle_input, args=(conn,), daemon=True).start()
        threading.Thread(target=self.stream_screen, args=(conn,), daemon=True).start()

    # ------------------ Server Lifecycle ------------------
    @time_it
    def stop(self):
        self.logger.info("\n[SHUTTING DOWN SERVER] Key 'esc' pressed.")
        self.server_running = False

        for conn in list(self.connections):
            try:
                conn.sendall(self.DISCONNECT_MSG.encode(self.FORMAT))
                time.sleep(0.1)
                conn.close()
            except Exception as e:
                self.logger.error(f" Could not close connection: {e}")
        self.connections.clear()

        keyboard.unhook_all()
        self.server.close()

    @time_it
    def run(self):
        self.server.listen()
        self.server.settimeout(1)
        self.logger.info(f"[LISTENING] Server is listening on {self.SERVER}:{self.PORT}")
        keyboard.add_hotkey("esc", self.stop)

        while self.server_running:
            while not self.queue.empty():
                self.lasted_copy = self.queue.get()
                pyperclip.copy(self.lasted_copy)
            
            try:
                conn, addr = self.server.accept()
                if not self.server_running:
                    conn.close()
                    break
                if len(self.connections) >= self.max_clients:
                    self.logger.warning(f"Connection limit of {self.max_clients} reached. Rejecting client: {addr}")
                    conn.close()
                    continue
                self.connections.append(conn)
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.start()
                self.logger.info(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
            except socket.timeout:
                continue
            except OSError:
                break

        self.logger.info("[SERVER STOPPED]")