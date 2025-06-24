from pyclbr import Function
from subprocess import call
import pybullet as p 

from PyQt5.QtCore import QObject, Qt, QEvent, QTimer
from PyQt5.QtGui  import QKeyEvent

class QKeyEventManager(QObject):
    def __init__(self, target_widget):
        super().__init__(target_widget)
        self._callbacks = {}    # key -> {"press": [], "hold": [], "release": []}
        self._hold_timers = {}  # key -> QTimer
        # install this object as an event filter on the widget
        target_widget.installEventFilter(self)

    def register_callback(self, key, on_press=None, on_hold=None, on_release=None):
        """
        key: Qt.Key_*, e.g. Qt.Key_W or ord('A')
        on_press/hold/release: callables taking a single int argument (the key code)
        """
        kc = key if isinstance(key, int) else key
        if kc not in self._callbacks:
            self._callbacks[kc] = {"press": [], "hold": [], "release": []}
        if on_press:
            self._callbacks[kc]["press"].append(on_press)
        if on_hold:
            self._callbacks[kc]["hold"].append(on_hold)
        if on_release:
            self._callbacks[kc]["release"].append(on_release)

    def eventFilter(self, obj, event):
        # intercept key events
        if isinstance(event, QKeyEvent):
            key = event.key()
            if event.type() == QEvent.KeyPress:
                # first, invoke press callbacks (only on autoRepeat==False)
                if not event.isAutoRepeat():
                    for cb in self._callbacks.get(key, {}).get("press", []):
                        cb(key)
                    # start a hold-timer if any hold callbacks are registered
                    if self._callbacks.get(key, {}).get("hold"):
                        timer = QTimer(self)
                        timer.setInterval(8)  # ms between hold-calls
                        timer.timeout.connect(lambda k=key: self._on_hold(k))
                        timer.start()
                        self._hold_timers[key] = timer
                return False

            elif event.type() == QEvent.KeyRelease:
                if not event.isAutoRepeat():
                    # stop any hold timer
                    if key in self._hold_timers:
                        self._hold_timers[key].stop()
                        del self._hold_timers[key]
                    # invoke release callbacks
                    for cb in self._callbacks.get(key, {}).get("release", []):
                        cb(key)
                return False

        return super().eventFilter(obj, event)

    def _on_hold(self, key):
        for cb in self._callbacks.get(key, {}).get("hold", []):
            cb(key)



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
            print(f"Key code: {key_code}, State: {state}")
            if key_code in self.callbacks:
                # basıldı
                if state & p.KEY_WAS_TRIGGERED:
                    self.pressed.add(key_code)
                    for cb in self.callbacks[key_code]["down"]:
                        print(f"Calling down callback for key code: {key_code}")
                        cb()
                # bırakıldı
                elif state & p.KEY_WAS_RELEASED:
                    if key_code in self.pressed:
 
                        self.pressed.remove(key_code)
                    for cb in self.callbacks[key_code]["up"]:
                        print(f"Calling up callback for key code: {key_code}")
 
                        cb()
        
        # hold callback’ları
        for key_code in list(self.pressed):
            for cb in self.callbacks.get(key_code, {}).get('hold', []):
                print(f"Calling hold callback for key code: {key_code}")
 
                cb()
