from examples.BaseRenderer import BaseRenderer

class RendererAPI():
    def __init__(self,renderer : BaseRenderer):
        self.renderer = renderer()

    def start(self):
        self.renderer.start_analizing()

    def bind_image(self,*args,**kwargs):
        self.renderer.bind_image(*args,**kwargs)

    def unbind_image(self,*args,**kwargs):
        self.renderer.unbind_image(*args, **kwargs)

    def get_input_file(self):
        self.renderer.get_input_file()