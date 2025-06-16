from pyclbr import Function
from subprocess import call
import pybullet as p 

class KeyEventManager:
    def __init__(self,):
        self.callbacks = {}
        self.pressed:set[int] = set()
        
    def register_callback(self,key:str,on_press:callable = None,on_release:callable =None,on_hold:callable=None):
        print(f"Registering key: {ord(key)}")
        if key not in self.callbacks:
            self.callbacks[ord(key)]  ={
                "down":[],
                "up":[],
                "hold":[]
            }
        if on_press:
            self.callbacks[ord(key)]["down"].append(on_press)
        if on_release:
            self.callbacks[ord(key)]["up"].append(on_release)
        if on_hold:
            self.callbacks[ord(key)]["hold"].append(on_hold)            
    def process_events(self):
        events = p.getKeyboardEvents()
        for key,state in events.items():
            if key in self.callbacks:
                if state & p.KEY_WAS_TRIGGERED:
                    self.pressed.add(key)
                    for callback in self.callbacks[key]["down"]:
                            callback()
                elif state & p.KEY_WAS_RELEASED:
                    if key in self.pressed:
                        self.pressed.remove(key)
                    for callback in self.callbacks[key]["up"]:
                            callback()
            
        for key in list(self.pressed):
            for cb in self.callbacks.get(key ,{}).get('hold',[]):
                cb()