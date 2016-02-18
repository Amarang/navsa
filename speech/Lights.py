import RPi.GPIO as gp
import threading
import atexit
import time
import math

class Lights:
    def __init__(self):
        self.PIN_BLUE = 17
        self.PIN_YELLOW = 27
        self.PIN_RED = 22
        gp.setmode(gp.BCM)
        gp.setup(self.PIN_BLUE,gp.OUT)
        gp.setup(self.PIN_YELLOW,gp.OUT)
        gp.setup(self.PIN_RED,gp.OUT)
        self.pin_high = False

        # self.latest_stopper = None

        atexit.register(self.cleanup)

    def color_to_pin(self, color):
        if color.startswith("b"): return self.PIN_BLUE
        elif color.startswith("y"): return self.PIN_YELLOW
        elif color.startswith("r"): return self.PIN_RED
        return self.PIN_BLUE

    def set_pin(self, pin, value):
        if self.pin_high and value: return
        if value: self.pin_high = True
        else: self.pin_high = False
        gp.output(pin, value)


    def action_quick_flash(self, color='blue', duration=0.7):
        # one quick flash
        pin = self.color_to_pin(color)
        self.set_pin(pin, 1)
        time.sleep(duration)
        self.set_pin(pin, 0)

    def action_flip(self, onoff="on", color='blue'):
        # flip on or off
        pin = self.color_to_pin(color)
        self.set_pin(pin, onoff=="on")

    def action_sine(self, duration=4.0, frequency=0.5, color='blue'):
        pin = self.color_to_pin(color)
        p = gp.PWM(pin,100) # LED pulsing frequency. don't touch
        updateFreq = 30 # update frequency (how smooth is the transition)
        p.start(0)
        for i in range(int(duration*updateFreq)):
            dt = 1.0/updateFreq
            # abs(sin(\omega t)), frequency divided by two because absolute value effectively doubles it
            val =  abs(100.0*math.sin(6.28*(1.0*frequency/2) * i*dt)) 
            p.ChangeDutyCycle(val)
            time.sleep(dt)
        p.stop()

    def action_pulse(self, duration=4.0, frequency=0.5, color='blue'):
        pin = self.color_to_pin(color)
        p = gp.PWM(pin,100) # LED pulsing frequency. don't touch
        updateFreq = 30 # update frequency (how smooth is the transition)
        p.start(0)
        for i in range(int(duration*updateFreq)):
            dt = 1.0/updateFreq
            # abs(sin(\omega t)), frequency divided by two because absolute value effectively doubles it
            val =  100.0*math.sin(6.28*(1.0*frequency/2) * i*dt)
            if val < 0: val = 0
            p.ChangeDutyCycle(val)
            time.sleep(dt)
        p.stop()

    def cleanup(self):
        gp.cleanup()

    def stop(self):
        self.set_pin(self.PIN_BLUE,0)
        self.set_pin(self.PIN_YELLOW,0)
        self.set_pin(self.PIN_RED,0)

    def start(self, action, blocking=False, **kwargs):
        dummy = lambda:None # dummy function: takes nothing, gives nothing

        if action == "flash": target = self.action_quick_flash
        elif action == "flip": target = self.action_flip
        elif action == "sine": target = self.action_sine
        elif action == "pulse": target = self.action_pulse
        else: 
            print "action", action, "not recognized."
            return dummy

        if blocking:
            target(**kwargs)
            return dummy

        else:
            listener_thread = threading.Thread(target=target, kwargs=kwargs)
            listener_thread.daemon = True
            listener_thread.start()
            
            def stopper():
                self.running = False
                listener_thread.join()

            # self.latest_stopper = stopper
            return stopper


if __name__=="__main__":
    led = Lights()


    stopper = led.start("pulse", duration=6.0, frequency=1, color='b', blocking=False)

    print "here"
    time.sleep(1)
    print "here 2"

    stopper()

