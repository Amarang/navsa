import RPi.GPIO as gp
import atexit
import time

class Lights:
    def __init__(self):
        self.PIN_BLUE = 17
        self.PIN_YELLOW = 27
        self.PIN_RED = 22
        gp.setmode(gp.BCM)
        gp.setup(self.PIN_BLUE,gp.OUT)
        gp.setup(self.PIN_YELLOW,gp.OUT)
        gp.setup(self.PIN_RED,gp.OUT)

        atexit.register(self.cleanup)

    def color_to_pin(self, color):
        if color.startswith("b"): return self.PIN_BLUE
        elif color.startswith("y"): return self.PIN_YELLOW
        elif color.startswith("r"): return self.PIN_RED
        return self.PIN_BLUE

    def flash(self, color='blue', duration=0.7):
        # one quick flash
        pin = self.color_to_pin(color)

        gp.output(pin,1)
        time.sleep(duration)
        gp.output(pin,0)

    def flip(self, onoff="off", color='blue'):
        # flip on or off
        pin = self.color_to_pin(color)

        gp.output(pin, onoff=="on")

    def cleanup(self):
        gp.cleanup()


if __name__=="__main__":
    led = Lights()
    led.flash(color="red")

    led.flip(onoff="on", color="b")
    time.sleep(3)
    led.flip(onoff="off")

# p = gp.PWM(17,100)
# p.start(0)
# p.ChangeDutyCycle(50)
# time.sleep(2)
# p.ChangeDutyCycle(100)
# p.stop()
# p.ChangeFrequency(100)
# gp.cleanup()
