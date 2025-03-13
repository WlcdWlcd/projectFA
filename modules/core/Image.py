import numpy as np
import cv2 as cv

from modules.core.avg_color import avg_color


class Image():
    def __init__(self,data:np.ndarray):
        self.data = data
        self.shape = lambda:data.shape
        self.height = lambda:self.shape()[0]
        self.width = lambda:self.shape()[1]
        self.channels = lambda:self.shape()[2]
        self.area = lambda:self.width()*self.height()
        self.size = lambda:self.area()*self.channels()

    def __copy__(self):
        return Image(self.data)


    def open(filepath):
        data = cv.imread(filepath)
        return Image(data)

    def create(width,height,channels = 3):
        if channels!=1:
            data = np.zeros((width,height, channels), np.uint8)
        else:
            data = np.zeros((width, height), np.uint8)
        return Image(data)

    def set_zeros_like(self):
        self.data = self.get_zeros_like().data
        return self

    def get_zeros_like(self):
        return Image(np.zeros_like(self.data))

    def get_resized(self, dsize=(0, 0), fx=1, fy=1):
        data = cv.resize(self.data.copy(), dsize, fx=fx, fy=fy)
        return Image(data)

    def resize(self, dsize=(0, 0), fx=1, fy=1):
        self.data = self.get_resized(dsize,fx,fy).data
        return self

    def get_cropped(self,p1:(int,int),p2:(int,int)):
        x1,x2 = p1[0],p2[0]
        y1,y2 = p1[1],p2[1]
        data = self.data[y1:y2,x1:x2]
        return Image(data)

    def crop(self,*args,**kwargs):
        self.data = self.get_cropped(*args,**kwargs).data
        return self

    def get_gray(self):
        return Image(cv.cvtColor(self.data,cv.COLOR_BGR2GRAY))

    def get_converted_color(self,code):
        return Image(cv.cvtColor(self.data,code))


    def convert_color(self,code):
        self.data = self.get_converted_color(code).data
        return self

    def gray(self):
        self.data=self.get_gray().data

    def thumb(self,*args,**kwargs):
        self.data = self.get_thumb(*args,**kwargs).data

    def get_thumb(self,*args,**kwargs):
        _,data = cv.threshold(self.data,*args,**kwargs)
        return Image(data)

    def gauss(self,*args,**kwargs):
        self.data = self.get_gauss(*args,**kwargs).data
        return self

    def get_gauss(self,ksize):
        data = cv.GaussianBlur(self.data,ksize,0)
        return Image(data)

    def find_contours(self):
        contours,_ = cv.findContours(self.data, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
        return contours

    def draw_contours(self,contours,idx=-1,color = (0,0,255),thickness=3):
        self.data = self.get_with_drawed_contours().data
        return self

    def get_with_drawed_contours(self,contours,idx=-1,color = (0,0,255),thickness=3):
        data = cv.drawContours(self.data.copy(), contours, idx, color, thickness)
        return Image(data)

    def draw_rect(self, p1:(int,int), p2:(int,int),color = (0,0,255)):
        self.data = self.get_with_drawed_rect(p1,p2,color).data
        return self

    def get_with_bounded_contours(self,contours,color = (0,0,255)):
        copy = self.__copy__()
        for contour in contours:
            epsillon = 0.01 * cv.arcLength(contour, True)
            approx = cv.approxPolyDP(contour, epsillon, True)
            #cv.drawContours(image,self.contour,0,color,4)
            x, y, w, h = cv.boundingRect(approx)
            copy.draw_rect((x,y),(x+w,y+h),color)
        return copy

    def draw_bonded_contours(self,contours,color = (0,0,255),thickness=3):
        self.data = self.get_with_drawed_contours(contours,color,thickness).data
        return self

    def get_with_drawed_rect(self, p1:(int,int), p2:(int,int),color = (0,0,255),thickness=3):
        x1, x2 = p1[0], p2[0]
        y1, y2 = p1[1], p2[1]
        data = cv.rectangle(self.data.copy(),(x1-1,y1-1),(x2,y2),color,thickness)
        return Image(data)

    def draw_circle(self,center,radius,color=(0,0,255),thickness=3):
        self.data = self.get_with_drawed_circle(center,radius,color,thickness).data
        return self

    def get_with_drawed_circle(self,center,radius,color=(0,0,255),thickness=3):
        data=cv.circle(self.data.copy(),center,radius,color,thickness)
        return Image(data)

    def get_with_drawed_enclosing_circles(self,contours,color = (0,0,255),thickness = 3):
        copy = self.__copy__()
        for contour in contours:


            (x,y),radius = cv.minEnclosingCircle(contour)
            center = (int(x),int(y))
            radius = int(radius)
            copy.draw_circle(center,radius,color,thickness)
        return copy

    def find_circles(self,method =cv.HOUGH_GRADIENT,dp=1,mindist=0,param1=50,param2=30,minRadius=0,maxRadius=0):
        circles = cv.HoughCircles(self.data,method=method,dp=dp,minDist=mindist,param1=param1,param2=param2,minRadius=minRadius,maxRadius=maxRadius)
        return circles.tolist()

    def get_with_mask(self,mask,color = [0,0,0]):
        data = self.data.copy()
        for col in range(mask.height()):
            for row in range(mask.width()):
                if (mask.data[col][row]==0).any():
                    data[col][row]=color
        return Image(data)


    def set_mask(self,mask,color = [0,0,0]):
        self.data = self.get_with_mask(mask,color).data
        return self

    def avg_color(self,exclude_colors = []):
        avg = avg_color(self.channels())
        count = 0
        for col in range(self.height()):
            for row in range(self.width()):
                pixel=self.data[col][row].tolist()
                if pixel not in exclude_colors:
                    avg+=pixel
                    count+=1
        avg/=count
        return list(avg)

    def avg_light(self,exclude_colors = []):
        arr = self.avg_color(exclude_colors)
        return sum(arr)//len(arr)

    def get_highlight_by_image_and_color(self,image,color,exclude_colors = [],lower_color=[0,0,255],upper_color = [0,255,0]):
        data = self.data.copy()
        for col in range(image.height()):
            for row in range(image.width()):
                pixel = image.data[col][row].tolist()
                if pixel not in exclude_colors:
                    avg_pixel_light = sum(pixel)//len(pixel)
                    if avg_pixel_light<color:
                        data[col][row] = lower_color
                    elif avg_pixel_light>color:
                        data[col][row] = upper_color
        return data
    def highlight_by_image_and_color(self,image,color,exclude_colors = [],lower_color=[0,0,255],upper_color = [0,255,0]):
        self.data = self.get_highlight_by_image_and_color(image,color,exclude_colors,lower_color,upper_color)
        return self