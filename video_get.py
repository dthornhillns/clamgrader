from threading import Thread
import cv2
import time

class VideoGet:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, cap, capRate):
        self.stream = cap
        self.capRate=capRate
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        self.fps=0
    def start(self):
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        newFrame = None
        frames=0
        startTime = time.time()
        while not self.stopped:
            if not self.grabbed:
                self.stream.set(cv2.CAP_PROP_POS_FRAMES, 0)

            (self.grabbed, newFrame) = self.stream.read()
            if self.grabbed:
                self.frame=newFrame
                frames+=1
                stopTime = time.time()
                if(stopTime>=0.250):
                    stop=time.time()
                    elapsed=stopTime-startTime
                    self.fps=frames/elapsed
                    frames=0
                    startTime = time.time()
            time.sleep(self.capRate)

    def stop(self):
        self.stopped = True
