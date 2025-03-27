from examples.BaseRenderer import BaseRenderer

from PyQt6 import uic
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets  import QApplication,QFileDialog
from PyQt6.QtGui import QPixmap,QImage
from PIL import Image, ImageQt

from App.analysisWorker import AnalysisWorker
from modules.tools.AnalysysConfig import AnalysisConfig

IMAGE_SELECTER_FILTER = "PNG Files (*.png);;JPG Files (*.jpg);;JPEG Files (*.jpeg);;"

class App():
    def __init__(self):
        Form, Window = uic.loadUiType(f"App/interface.ui")
        self.app = QApplication([])
        self.window = Window()
        self.form = Form()
        self.form.setupUi(self.window)
        self.connect_buttons()



    def connect_buttons(self):
        self.form.select_file_push_button.clicked.connect(self.open_dialog)
        self.selected_file = ''

        self.form.start_push_button.clicked.connect(self.start_analysis)

    def start_analysis(self):
        try:
            self.thread = QThread()
            self.worker = AnalysisWorker()
            self.generate_analysis_config()

            self.worker.set_path(self.selected_file)
            self.worker.set_config(self.config)

            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.image_signal.connect(self.update_image)
            self.worker.percent_signal.connect(self.update_percent)
            print("starting")

            self.thread.start()
            print("thread runned")
        except Exception as e:
            self.worker.deleteLater()
            self.thread.deleteLater()
            print(e)

    def generate_analysis_config(self):
        thresh   = self.form.thresh_slider.value()
        center_deltaX = self.form.c1_deltax_slider.value()
        center_deltaY = self.form.c1_deltay_slider.value()
        deltaR =  self.form.deltaR_slider.value()




        self.config = AnalysisConfig(
                                thresh   = thresh,
                                center_deltaX = center_deltaX,
                                center_deltaY = center_deltaY,
                                deltaR = deltaR,
        )


    def update_percent(self,bad_pixels,good_pixels):
        percent = 100 * (bad_pixels) / (good_pixels + bad_pixels)
        self.form.PrersentageLabel.setText(f"процент загрязнения: {percent :.2f}%")

    def update_image(self,image):
        w = self.form.ImageLabel.width()
        h = self.form.ImageLabel.height()
        pixmap = QPixmap.fromImage(image)
        self.form.ImageLabel.setPixmap(pixmap.scaled(w,h))


    def open_dialog(self):
        fname,_ = QFileDialog.getOpenFileName(
            filter = IMAGE_SELECTER_FILTER
        )
        self.form.selected_file_label.setText(fname)
        self.selected_file = fname

    def get_input_file(self):
        if self.selected_file !='':
            return self.selected_file
        return False

    def start(self):
        self.window.show()
        self.app.exec()



