from PyQt6.QtCore import QThread, pyqtSignal, QObject
from modules.core.Image import Image
import cv2 as cv
from modules.tools.AnalysysConfig import AnalysisConfig


from PyQt6.QtGui import QImage


class Pixels_counter:
    def __init__(self):
        self.count = 0
        self.bad = 0

class Circle():
    def __init__(self,center,radius):
        self.center = center
        self.radius = radius

class Ring(Circle):
    def __init__(self,center,radius,small_radius):
        super().__init__(center,radius)
        self.small_radius = small_radius

class AnalysisWorker(QObject):
    finished = pyqtSignal()
    #percent_signal = pyqtSignal(int,int)
    core_signal = pyqtSignal(int,int)
    shell_signal = pyqtSignal(int, int)
    update_signal = pyqtSignal(str)  # text signal
    image_signal = pyqtSignal(QImage)  # image signal

    def set_path(self,path):
        self.path=path


    def set_config(self,config):
        self.config = config

    def init_images(self):
        self.image = Image.open(self.path)
        self.gray = self.image.get_gray()
        self.gaus = self.gray.get_gauss((5,5))
        print("THRESH",self.config.thresh)
        self.thumb = self.gaus.get_thumb(self.config.thresh, 255, cv.THRESH_TOZERO_INV)



    def get_circle(self):
        circles_image = self.image.__copy__()
        circles = self.thumb.find_circles(mindist=max(self.gray.width(), self.gray.height()),
                                          dp=1,
                                          param1=50,
                                          param2=0.9,
                                          maxRadius=min(self.gray.width(), self.gray.height()) // 5,
                                          minRadius=min(self.gray.width(), self.gray.height()) // 6,
                                          )[0]

        circle = circles[0]
        circle = list(map(int, circle))
        center = circle[0:2]
        radius = int(circle[2]) - 2

        #circles_image.draw_circle(center, radius)

        center[0] += self.config.center_deltaX
        center[1] += self.config.center_deltaY
        radius += self.config.deltaR

        return Circle(center,radius)

    def get_crop(self,circle):
        p1 = list(map(lambda x: x - circle.radius, circle.center))
        p2 = list(map(lambda x: x + circle.radius + 1, circle.center))
        # definding cropped image
        crop = self.image.get_cropped(p1, p2)
        return crop

    def iterate_circle(self,image,ring,signal,good_color = (0,255,0),bad_color = (0,0,255)):
        delta_light = -15
        pixels = Pixels_counter()
        for dr in range(ring.small_radius, ring.radius, 1):
            coords = get_circle_coords(ring.center, dr, dphi=0.005)
            avg_light = 0

            for i in coords:
                x, y = i
                pixel = self.crop.data[x][y].tolist()
                avg_light += sum(pixel)
            avg_light //= len(coords) * self.crop.channels()
            for i in coords:
                x, y = i
                pixel = self.crop.data[x][y].tolist()
                if sum(pixel) // 3 < avg_light + delta_light:
                    image.data[x][y] = bad_color
                    pixels.bad += 1
                else:
                    image.data[x][y] = good_color

                pixels.count += 1

            signal.emit(pixels.bad, pixels.count)
            self.send_image(image)

    def run(self):
        try:
            self.init_images()
            circle = self.get_circle()
            self.crop = self.get_crop(circle)
            crop_scale = 3
            self.crop.resize(fx=crop_scale, fy=crop_scale)

            crop_circle =Circle((crop_scale * self.crop.width() // 2, crop_scale * self.crop.height() // 2),
                                     crop_scale * self.crop.width() // 2)

            # self.RENDERER_API.bind_image("cropped", self.crop)



            h=Image(self.crop.data.copy())
            # self.RENDERER_API.bind_image("highlighted", h)


            pixels = Pixels_counter()
            print(type(circle))

            core_ring = Ring(crop_circle.center,crop_circle.radius//2,0)
            shell_ring = Ring(crop_circle.center,crop_circle.radius,core_ring.radius)


            print("starting iterate")
            self.iterate_circle(h,core_ring,self.core_signal,)
            self.iterate_circle(h,shell_ring,self.shell_signal,bad_color = (0,255,255),good_color=(0,255,0))
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
