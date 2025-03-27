from API.rendererAPI import RendererAPI
from examples.CVRenderer import CVrenderer
from modules.core.Image import Image
import cv2 as cv
import math
from threading import Thread

class App:
    def __init__(self):
        self.RENDERER_API = RendererAPI(CVrenderer)
        t = Thread(target = lambda : self.RENDERER_API.start())
        t.start()
        print(123)
        self.image = Image.open("/src/LC/LC-12.png")
        self.gray = self.image.get_gray()
        self.gaus = self.gray.get_gauss((5,5))
        self.thumb = self.gaus.get_thumb(100, 255, cv.THRESH_TOZERO_INV)


    def run(self):
        print("running")
        self.RENDERER_API.bind_image("image", self.image)

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
        p1=list(map(lambda x: x-radius+1,center))
        p2=list(map(lambda x: x+radius+1,center))

        self.RENDERER_API.bind_image("circles", self.circles_image)

        f=3
        self.crop = self.image.get_cropped(p1,p2)
        self.crop.resize(fx=3,fy=3)
        center = (f*self.crop.width()//2,f*self.crop.height()//2)
        radius = f*self.crop.width()//2
        self.RENDERER_API.bind_image("cropped", self.crop)

        # ПЕРЕНЕСТИ В ФУНКЦИЮ!!!
        h=Image(self.crop.data.copy())
        self.RENDERER_API.bind_image("highlighted", h)
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

        print(f"процент загрязнения: {100*(bad_pixels)/(good_pixels+bad_pixels):.2f}%")



def get_circle_coords(center:(int,int),radius:int,dphi=0.1):
    x0,y0=center
    # Generated vertices
    positions = []
    t = 0
    while t < 2 * math.pi:
        positions.append((int(radius * math.cos(t)) + x0, int(radius * math.sin(t) + y0)))
        t += dphi
    return tuple(positions)



if __name__ == "__main__":
    app = App()
    app.run()