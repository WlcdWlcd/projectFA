from examples.BaseRenderer import BaseRenderer

from threading import Thread
import cv2 as cv

class CVrenderer(BaseRenderer):
    def start(self):
        if not self.is_running:
            t = Thread(target=lambda: self.thread_target())
            t.start()

    def thread_target(self):
        self.is_running = True
        while self.is_running:
            try:
                for image_name,image in self.images.items():
                    cv.imshow(image_name,image)
                if (self.p() & 0xFF) == ord('q'):
                        cv.destroyAllWindows()
                        self.is_running = False
            except Exception as e:
                print(image_name)
                print(f"{e}")

    def p(self):
        k = cv.waitKey(1)
        return k
