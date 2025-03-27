from modules.core.Image import Image

class BaseRenderer():
    def __init__(self):
        self.images = {}
        self.is_running = False

    def bind_image(self,image_name,image:Image):
        self.images[image_name] = image.data

    def unbind_image(self,image_name):
        self.images.pop(image_name)

    def start(self):
        pass
