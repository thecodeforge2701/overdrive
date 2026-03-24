import socket
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line
from kivy.properties import StringProperty
from plyer import accelerometer

# --- GLOBAL SETTINGS ---
Window.rotation = 0
Window.clearcolor = (0.05, 0.05, 0.08, 1)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVER_IP = ''
SERVER_PORT = 5000

# --- NETWORKING ---
def send_msg(msg):
    try:
        if SERVER_IP:
            sock.sendto(msg.encode('utf-8'), (SERVER_IP, int(SERVER_PORT)))
    except:
        return None

# --- NEON RETRO THEMES ---
THEMES = {
    'cyan': ([0.0, 0.6, 0.8, 1], [0.2, 0.9, 1.0, 1], [0.0, 0.3, 0.5, 1]),
    'pink': ([0.8, 0.1, 0.4, 1], [1.0, 0.3, 0.6, 1], [0.5, 0.0, 0.2, 1]),
    'green': ([0.2, 0.7, 0.2, 1], [0.4, 0.9, 0.4, 1], [0.1, 0.4, 0.1, 1]),
    'blue': ([0.2, 0.3, 0.9, 1], [0.4, 0.5, 1.0, 1], [0.1, 0.1, 0.6, 1]),
    'yellow': ([0.8, 0.7, 0.1, 1], [1.0, 0.9, 0.3, 1], [0.5, 0.4, 0.0, 1]),
    'grey': ([0.25, 0.25, 0.3, 1], [0.4, 0.4, 0.45, 1], [0.15, 0.15, 0.18, 1])
}

# --- CUSTOM UI COMPONENTS ---
class PixelTechButton(Button):
    theme_key = StringProperty('grey')
    
    def __init__(self, theme='grey', **kwargs):
        super().__init__(**kwargs)
        self.theme_key = theme
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.background_down = ''
        
        # Default to solid white if color isn't passed
        if 'color' not in kwargs:
            self.color = (1, 1, 1, 1)
            
        self.bold = True
        self.bind(pos=self.draw_btn, size=self.draw_btn, state=self.draw_btn)
        
    def draw_btn(self, *args):
        self.canvas.before.clear()
        base, rim, shadow = THEMES.get(self.theme_key, THEMES['grey'])
        is_down = self.state == 'down'
        off_y = (-4) if is_down else 0
        
        if is_down:
            base = [min(1.0, c + 0.2) for c in base[:3]] + [1]
            rim = [min(1.0, c + 0.2) for c in rim[:3]] + [1]
            
        x, y = (self.x, self.y + off_y)
        w, h = (self.width, self.height)
        s = 8
        
        with self.canvas.before:
            Color(0.02, 0.02, 0.02, 1)
            Rectangle(pos=(x, y + s), size=(w, h - 2 * s))
            Rectangle(pos=(x + s, y), size=(w - 2 * s, h))
            Rectangle(pos=(x + s, y + s), size=(w - 2 * s, h - 2 * s))
            Color(*base)
            Rectangle(pos=(x + 4, y + s + 4), size=(w - 8, h - 2 * s - 8))
            Rectangle(pos=(x + s + 4, y + 4), size=(w - 2 * s - 8, h - 8))
            Color(*rim)
            Rectangle(pos=(x + s + 4, y + h - s - 4), size=(w - 2 * s - 8, 4))
            Color(*shadow)
            Rectangle(pos=(x + s + 4, y + s), size=(w - 2 * s - 8, 4))
            Color(*base)
            Rectangle(pos=(x + s, y + s), size=(4, 4))
            Rectangle(pos=(x + w - s - 4, y + s), size=(4, 4))
            Rectangle(pos=(x + s, y + h - s - 4), size=(4, 4))
            Rectangle(pos=(x + w - s - 4, y + h - s - 4), size=(4, 4))

class TechTouchPad(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (1, 1, 1, 0.3)
        self.bold = True
        self.bind(pos=self.draw_pad, size=self.draw_pad)
        
    def draw_pad(self, *args):
        self.canvas.before.clear()
        x, y = (self.x, self.y)
        w, h = (self.width, self.height)
        s = 10
        with self.canvas.before:
            Color(0.02, 0.02, 0.02, 1)
            Rectangle(pos=(x, y + s), size=(w, h - 2 * s))
            Rectangle(pos=(x + s, y), size=(w - 2 * s, h))
            Color(0.08, 0.1, 0.12, 1)
            Rectangle(pos=(x + 4, y + s), size=(w - 8, h - 2 * s))
            Rectangle(pos=(x + s, y + 4), size=(w - 2 * s, h - 8))
            Color(0.0, 0.8, 0.9, 0.15) 
            for i in range(1, 4):
                Line(points=[x + 4, y + i * h / 4, x + w - 4, y + i * h / 4], width=1)
                Line(points=[x + i * w / 4, y + 4, x + i * w / 4, y + h - 4], width=1)
            Color(0.0, 0.8, 0.9, 0.6)
            Line(points=[x + w / 2, y + 20, x + w / 2, y + h - 20], width=1.5)
            Line(points=[x + 20, y + h / 2, x + w - 20, y + h / 2], width=1.5)
            
    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            send_msg(f'MOUSE_MOVE:{touch.dx},{touch.dy}')

# --- SCREENS ---
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        layout.add_widget(Label(
            text='OVERDRIVE WHEEL', 
            font_size=45, 
            bold=True, 
            color=(1, 0.2, 0.6, 1)
        ))
        
        self.ip_input = TextInput(
            text='', 
            hint_text='[ Server IP Address ]',
            halign='center',
            multiline=False, 
            font_size=30, 
            size_hint=(1, 0.2), 
            background_color=(0.1, 0.1, 0.12, 1), 
            foreground_color=(0.0, 0.8, 0.9, 1), 
            hint_text_color=(0.3, 0.4, 0.5, 1),
            cursor_color=(1, 0.2, 0.6, 1)
        )
        layout.add_widget(self.ip_input)
        
        self.port_input = TextInput(
            text='5000', 
            hint_text='[ Port ]',
            halign='center',
            multiline=False, 
            font_size=30, 
            size_hint=(1, 0.2), 
            background_color=(0.1, 0.1, 0.12, 1), 
            foreground_color=(0.0, 0.8, 0.9, 1),
            cursor_color=(1, 0.2, 0.6, 1)
        )
        layout.add_widget(self.port_input)
        
        btn = PixelTechButton(text='INITIALIZE', theme='cyan', font_size=35, size_hint=(1, 0.3))
        btn.bind(on_press=self.connect)
        layout.add_widget(btn)
        self.add_widget(layout)
        
    def connect(self, instance):
        global SERVER_IP
        global SERVER_PORT
        SERVER_IP = self.ip_input.text.strip()
        SERVER_PORT = self.port_input.text.strip()
        self.manager.current = 'game'

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        self.gyro_active = True
        
        sw = Switch(active=True, size_hint=(None, None), size=(100, 50), pos_hint={'center_x': 0.5, 'top': 0.95})
        sw.bind(active=self.toggle_gyro)
        self.layout.add_widget(sw)
        
        tp = TechTouchPad(text='TRACK', pos_hint={'center_x': 0.5, 'center_y': 0.55}, size_hint=(0.25, 0.35))
        self.layout.add_widget(tp)
        
        def make_btn(text, pos, size, cmd, theme='grey'):
            btn = PixelTechButton(text=text, theme=theme, pos_hint=pos, size_hint=size, color=(1, 1, 1, 0.4))
            
            def on_p(instance):
                send_msg(f'{cmd}:DOWN')
                
            def on_r(instance):
                send_msg(f'{cmd}:UP')
                
            btn.bind(on_press=on_p)
            btn.bind(on_release=on_r)
            self.layout.add_widget(btn)
            
        make_btn('BRAKE', {'x': 0.02, 'top': 0.98}, (0.3, 0.25), 'BTN_LB', theme='pink')
        make_btn('GAS', {'right': 0.98, 'top': 0.98}, (0.3, 0.25), 'BTN_RB', theme='green')
        make_btn('LMB', {'right': 0.49, 'top': 0.36}, (0.12, 0.12), 'LMB', theme='cyan')
        make_btn('RMB', {'x': 0.51, 'top': 0.36}, (0.12, 0.12), 'RMB', theme='cyan')
        make_btn('Y', {'right': 0.85, 'y': 0.45}, (0.08, 0.15), 'BTN_Y', theme='yellow')
        make_btn('A', {'right': 0.85, 'y': 0.1}, (0.08, 0.15), 'BTN_A', theme='green')
        make_btn('X', {'right': 0.94, 'y': 0.28}, (0.08, 0.15), 'BTN_X', theme='blue')
        make_btn('B', {'right': 0.76, 'y': 0.28}, (0.08, 0.15), 'BTN_B', theme='pink')
        make_btn('U', {'x': 0.13, 'y': 0.45}, (0.08, 0.15), 'BTN_UP', theme='grey')
        make_btn('D', {'x': 0.13, 'y': 0.1}, (0.08, 0.15), 'BTN_DOWN', theme='grey')
        make_btn('L', {'x': 0.04, 'y': 0.28}, (0.08, 0.15), 'BTN_LEFT', theme='grey')
        make_btn('R', {'x': 0.22, 'y': 0.28}, (0.08, 0.15), 'BTN_RIGHT', theme='grey')
        make_btn('SLCT', {'center_x': 0.4, 'y': 0.05}, (0.15, 0.1), 'BTN_SELECT', theme='grey')
        make_btn('STRT', {'center_x': 0.6, 'y': 0.05}, (0.15, 0.1), 'BTN_START', theme='grey')
        
        self.add_widget(self.layout)
        
        try:
            accelerometer.enable()
            Clock.schedule_interval(self.update_gyro, 1.0 / 60.0) 
        except:
            pass
            
    def toggle_gyro(self, instance, value):
        self.gyro_active = value
        if not value:
            send_msg('STEER:0')
            
    def update_gyro(self, dt):
        if not self.gyro_active:
            return None
        try:
            val = accelerometer.acceleration
            if val and len(val) > 1 and val[1] is not None:
                tilt = val[1] / 9.81 * 90
                send_msg(f'STEER:{tilt:.2f}')
        except:
            pass

class ControllerApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(GameScreen(name='game'))
        return sm

if __name__ == '__main__':
    ControllerApp().run()
