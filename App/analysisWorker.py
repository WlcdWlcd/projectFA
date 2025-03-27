from PyQt6.QtCore import QThread, pyqtSignal, QObject
from modules.core.Image import Image
import cv2 as cv
from modules.tools.AnalysysConfig import AnalysisConfig


from PyQt6.QtGui import QImage


class AnalysisWorker(QObject):
    finished = pyqtSignal()
    percent_signal = pyqtSignal(int,int)
    update_signal = pyqtSignal(str)  # text signal
    image_signal = pyqtSignal(QImage)  # image signal
    def set_path(self,path):
        print(path)
        self.path=path


    def set_config(self,config):
        self.config = config

    def init_images(self):
        self.image = Image.open(self.path)
        self.gray = self.image.get_gray()
        self.gaus = self.gray.get_gauss((5,5))
        print("THRESH",self.config.thresh)
        self.thumb = self.gaus.get_thumb(self.config.thresh, 255, cv.THRESH_TOZERO_INV)


    def run(self):
        try:
            print("run from thread")
            self.init_images()
            self.circles_image = self.image.__copy__()
            circles = self.thumb.find_circles(mindist = max(self.gray.width(),self.gray.height()),
                                             dp=1,
                                             param1=50,
                                             param2=0.9,
                                             maxRadius=min(self.gray.width(),self.gray.height())//5,
                                             minRadius=min(self.gray.width(),self.gray.height())//6,
                                             )[0]

            circle = circles[0]
            circle = list(map(int, circle))
            center = circle[0:2]
            radius = int(circle[2])-2

            self.circles_image.draw_circle(center, radius)

            center[0]+=self.config.center_deltaX
            center[1]+=self.config.center_deltaY
            radius+=self.config.deltaR

            p1=list(map(lambda x: x-radius,center))
            p2=list(map(lambda x: x+radius+1,center))

            f = 3
            self.crop = self.image.get_cropped(p1, p2)
            self.crop.resize(fx=3, fy=3)
            center = (f * self.crop.width() // 2, f * self.crop.height() // 2)
            radius = f * self.crop.width() // 2
            # self.RENDERER_API.bind_image("cropped", self.crop)

            h=Image(self.crop.data.copy())
            # self.RENDERER_API.bind_image("highlighted", h)
            delta_light = -15
            bad_pixels=0
            good_pixels=0
            for dr in range(0,radius,1):
                coords = get_circle_coords(center,dr,dphi=0.005)
                avg_light=0

                for i in coords:
                    x,y=i
                    pixel = self.crop.data[x][y].tolist()
                    avg_light+=sum(pixel)
                avg_light//=len(coords)*self.crop.channels()
                for i in coords:
                    x,y=i
                    pixel = self.crop.data[x][y].tolist()
                    if sum(pixel)//3<avg_light+delta_light:
                        h.data[x][y]=[0,0,255]
                        bad_pixels+=1
                    else:
                        h.data[x][y]=[0,255,0]
                        good_pixels+=1
                self.percent_signal.emit(bad_pixels, good_pixels)
                self.send_image(h)
            self.finished.emit()
        except Exception as e:
            print(e)
            self.finished.emit()

    def send_image(self,image):
        frame_rgb = cv.cvtColor(image.data, cv.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        q_image = QImage(frame_rgb.data,
                        w,
                        h,
                        ch * w,
                        QImage.Format.Format_RGB888)
        # Байтов на строку (3 канала * ширина)

        self.image_signal.emit(q_image.copy())


def get_circle_coords(center:(int,int),radius:int,dphi=0.1):
    import math
    x0,y0=center
    # Generated vertices
    positions = []
    t = 0
    while t < 2 * math.pi:
        positions.append((int(radius * math.cos(t)) + x0, int(radius * math.sin(t) + y0)))
        t += dphi
    return tuple(positions)
