from pyclbr import Function
from subprocess import call
import pybullet as p 




class KeyEventManager:
    VK_SHIFT   = 0xFF1A  # Virtual key code for Shift
    VK_CONTROL = 0xFF1B  # Virtual key code for Control
    
    def __init__(self):
        self.callbacks = {}      # key_code -> {"down":[], "up":[], "hold":[]}
        self.pressed: set[int] = set()
        
    def register_callback(self,
                          key: str | int,
                          on_press:   callable = None,
                          on_release: callable = None,
                          on_hold:    callable = None):

        # Anahtarın kodunu belirle
        if isinstance(key, str):
            k = key.lower()
            if k == 'shift':
                code = self.VK_SHIFT
            elif k in ('ctrl','control'):
                code = self.VK_CONTROL
            elif len(key) == 1:
                code = ord(key)
            else:
                raise ValueError(f"Tanınmayan key tanımı: {key!r}")
        elif isinstance(key, int):
            code = key
        else:
            raise TypeError(f"Key tipi str veya int olmalı, verildi: {type(key)}")
        
        # callback listesini hazırla
        if code not in self.callbacks:
            self.callbacks[code] = {"down": [], "up": [], "hold": []}
        if on_press:
            self.callbacks[code]["down"].append(on_press)
        if on_release:
            self.callbacks[code]["up"].append(on_release)
        if on_hold:
            self.callbacks[code]["hold"].append(on_hold)            
    
    def process_events(self):
        events = p.getKeyboardEvents()
        # down / up tetikleme
        for key_code, state in events.items():
            if key_code in self.callbacks:
                # basıldı
                if state & p.KEY_WAS_TRIGGERED:
                    self.pressed.add(key_code)
                    for cb in self.callbacks[key_code]["down"]:
                        cb()
                # bırakıldı
                elif state & p.KEY_WAS_RELEASED:
                    if key_code in self.pressed:
                        self.pressed.remove(key_code)
                    for cb in self.callbacks[key_code]["up"]:
                        cb()
        
        # hold callback’ları
        for key_code in list(self.pressed):
            for cb in self.callbacks.get(key_code, {}).get('hold', []):
                cb()
