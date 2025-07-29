import cv2
import numpy as np
import mss

class ScreenCapture:
    def __init__(self, monitor_index=1):
        self.sct = mss.mss()
        monitors = self.sct.monitors
        if monitor_index >= len(monitors):
            raise ValueError(f"Monitor index {monitor_index} Not available. There is {len(monitors)-1} monitor detected.")
        self.monitor = monitors[monitor_index]
        print(f"Capturing Monitor: {self.monitor}")

    def capture_and_show(self):
        print("Showing real -time capture. Press 'Q' to leave.")
        while True:
            img = np.array(self.sct.grab(self.monitor))
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            cv2.imshow('Screen Capture', img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Leaving the capture.")
                break

        cv2.destroyAllWindows()