import RPi.GPIO as gp
import time
import random
import colorsys
import atexit



class Lights():
    def __init__(self):
        self.PIN_R = 22
        self.PIN_G = 27
        self.PIN_B = 17
        self.HI = 1
        self.LO = 0

        self.p1 = None
        self.p2 = None
        self.p3 = None

        gp.setmode(gp.BCM)
        gp.setup(self.PIN_R,self.LO)
        gp.setup(self.PIN_G,self.LO)
        gp.setup(self.PIN_B,self.LO)

        atexit.register(self.cleanup)

    def rgb_mult(self,rgb,mult=100.0/255):
        r,g,b = rgb
        return map(lambda x: int(mult*x), list(rgb))

    def cleanup(self):
        gp.cleanup()

    def start(self):
        self.p1 = gp.PWM(self.PIN_R,200)
        self.p1.start(0)

        self.p2 = gp.PWM(self.PIN_G,200)
        self.p2.start(0)

        self.p3 = gp.PWM(self.PIN_B,200)
        self.p3.start(0)

    def switch_color_hls(self,hue,lum=0.5,sat=0.9):
        # luminance from 0.0 to 0.7 depending on volume
        # hue depends on frequency

        rgb = colorsys.hls_to_rgb(hue,lum,sat)
        r,g,b = self.rgb_mult(rgb, 100)
        self.switch_color(r,g,b)


    def switch_color_rgb(self,r,g,b):
        r = int(r)
        g = int(g)
        b = int(b)

        self.p1.ChangeDutyCycle(min(100,r))
        self.p2.ChangeDutyCycle(min(100,g))
        self.p3.ChangeDutyCycle(min(100,b))

        # lum = 0.5
        # sat = 0.9
        # N = 200
        # secs = 2.0
        # for hue in range(0,N):
        #     hue = 1.0*hue / N
        #     # rgb = [random.randint(10,255) for _ in range(3)]
        #     rgb = colorsys.hls_to_rgb(hue,lum,sat)
        #     rgb100 = rgb_mult(rgb, 100)
        #     p1.ChangeDutyCycle(rgb100[0])
        #     p2.ChangeDutyCycle(rgb100[1])
        #     p3.ChangeDutyCycle(rgb100[2])
        #     time.sleep(secs/N)


if __name__ == "__main__":
    led = Lights()
    led.start()

    lum = 0.5
    sat = 0.9
    N = 200
    secs = 2.0
    for hue in range(0,N):
        hue = 1.0*hue/N
        led.switch_color(hue, lum, sat)
        time.sleep(secs/N)
