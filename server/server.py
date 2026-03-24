import socket
import vgamepad as vg
import mouse
import threading
import time
import customtkinter as ctk
import sys
import os

UDP_PORT = 5000

# Set up the UI Theme
ctk.set_appearance_mode('Dark')
ctk.set_default_color_theme('blue')

class RacingServer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.last_packet_time = 0
        self.client_ip = None
        self.running = True
        
        # --- UI Header ---
        self.header = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color='#1a1a1a')
        self.header.pack(fill='x')
        self.title_label = ctk.CTkLabel(self.header, text='OVERDRIVE SERVER', font=('Roboto Medium', 20), text_color='#00E5FF')
        self.title_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # --- IP Display Area ---
        self.ip_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.ip_frame.pack(pady=30)
        self.lbl_instruction = ctk.CTkLabel(self.ip_frame, text='ENTER THIS IP IN PHONE APP:', font=('Arial', 12), text_color='gray')
        self.lbl_instruction.pack()
        
        self.local_ip = self.get_local_ip()
        self.lbl_ip = ctk.CTkLabel(self.ip_frame, text=self.local_ip, font=('Roboto', 32, 'bold'), text_color='white')
        self.lbl_ip.pack(pady=5)
        
        self.btn_copy = ctk.CTkButton(self.ip_frame, text='COPY IP', width=80, height=25, fg_color='#333', hover_color='#444', command=self.copy_ip)
        self.btn_copy.pack(pady=5)
        
        # --- Status Area ---
        self.status_frame = ctk.CTkFrame(self, fg_color='#222', corner_radius=15, width=300, height=80)
        self.status_frame.pack(pady=20)
        self.status_frame.pack_propagate(False)
        
        self.lbl_status_icon = ctk.CTkLabel(self.status_frame, text='🔴', font=('Arial', 24))
        self.lbl_status_icon.place(relx=0.15, rely=0.5, anchor='center')
        self.lbl_status_text = ctk.CTkLabel(self.status_frame, text='DISCONNECTED', font=('Roboto', 14, 'bold'), text_color='#ff5555')
        self.lbl_status_text.place(relx=0.5, rely=0.4, anchor='center')
        self.lbl_client_ip = ctk.CTkLabel(self.status_frame, text='Waiting for phone...', font=('Arial', 11), text_color='gray')
        self.lbl_client_ip.place(relx=0.5, rely=0.7, anchor='center')
        
        self.lbl_footer = ctk.CTkLabel(self, text=f'Port: {UDP_PORT} | v3.0', font=('Arial', 10), text_color='#444')
        self.lbl_footer.pack(side='bottom', pady=10)
        
        # --- Gamepad & Networking Initialization ---
        self.gamepad = vg.VX360Gamepad()
        
        # Start the background listener thread
        self.thread = threading.Thread(target=self.udp_listener, daemon=True)
        self.thread.start()
        
        # Start the UI update loop
        self.check_connection()

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return '127.0.0.1'

    def copy_ip(self):
        self.clipboard_clear()
        self.clipboard_append(self.local_ip)
        self.btn_copy.configure(text='COPIED!', fg_color='#00aa00')
        self.after(2000, lambda: self.btn_copy.configure(text='COPY IP', fg_color='#333'))

    def check_connection(self):
        time_diff = time.time() - self.last_packet_time
        if self.last_packet_time > 0 and time_diff < 3.0:
            self.lbl_status_icon.configure(text='🟢')
            self.lbl_status_text.configure(text='SYSTEM ONLINE', text_color='#00ff00')
            self.lbl_client_ip.configure(text=f'Receiving data from {self.client_ip}')
            self.status_frame.configure(fg_color='#1a331a')
        else:
            self.lbl_status_icon.configure(text='🔴')
            self.lbl_status_text.configure(text='DISCONNECTED', text_color='#ff5555')
            self.lbl_client_ip.configure(text='Waiting for phone...')
            self.status_frame.configure(fg_color='#331a1a')
            
        self.after(500, self.check_connection)

    def udp_listener(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', UDP_PORT))
        
        # Button Mapping Dictionary for cleaner logic
        BTN_MAP = {
            'A': vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
            'B': vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
            'X': vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
            'Y': vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
            'START': vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
            'SELECT': vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
            'UP': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
            'DOWN': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
            'LEFT': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
            'RIGHT': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT
        }

        # The loop the decompiler accidentally deleted
        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                self.last_packet_time = time.time()
                self.client_ip = addr[0]
                message = data.decode('utf-8')
                
                if ':' not in message:
                    continue
                    
                tag, val = message.split(':', 1)
                
                # --- MOUSE MOVEMENT ---
                if tag == 'MOUSE_MOVE':
                    try:
                        dx, dy = map(float, val.split(','))
                        mouse.move(dx * 1.5, -dy * 1.5, absolute=False, duration=0)
                    except ValueError:
                        pass

                # --- MOUSE CLICKS ---
                elif tag == 'LMB':
                    mouse.press('left') if val == 'DOWN' else mouse.release('left')
                elif tag == 'RMB':
                    mouse.press('right') if val == 'DOWN' else mouse.release('right')

                # --- STEERING SENSOR ---
                elif tag == 'STEER':
                    steer_val = int(float(val) * 364)
                    # Clamp the value so it doesn't crash the virtual joystick
                    steer_val = max(-32768, min(32767, steer_val)) 
                    self.gamepad.left_joystick(x_value=steer_val, y_value=0)

                # --- GAMEPAD BUTTONS & TRIGGERS ---
                elif tag.startswith('BTN_'):
                    btn_name = tag.replace('BTN_', '')
                    is_down = (val == 'DOWN')

                    if btn_name == 'LB':
                        self.gamepad.left_trigger(value=255 if is_down else 0)
                    elif btn_name == 'RB':
                        self.gamepad.right_trigger(value=255 if is_down else 0)
                    elif btn_name in BTN_MAP:
                        if is_down:
                            self.gamepad.press_button(button=BTN_MAP[btn_name])
                        else:
                            self.gamepad.release_button(button=BTN_MAP[btn_name])

                # Push the state to the virtual controller
                self.gamepad.update()
                
            except Exception as e:
                print(f"Error processing packet: {e}")

if __name__ == '__main__':
    app = RacingServer()
    app.mainloop()
