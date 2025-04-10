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

            #подключение сигнала обновления изображения
            self.worker.image_signal.connect(self.update_image)

            #подключение сигналов обновления процентов
            self.worker.core_signal.connect(self.core_percetange_update)
            self.worker.shell_signal.connect(self.shell_percetange_update)

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




    def core_percetange_update(self,bad_pixels,pixels_count):
        percent = 100 * (bad_pixels) / pixels_count
        self.form.core_label.setText(f"процент загрязнения на ядре(??): {percent :.2f}% { 'критично' if percent>5 else '' }")

    def shell_percetange_update(self,bad_pixels,pixels_count):
        percent = 100 * (bad_pixels) / pixels_count
        self.form.shell_label.setText(f"процент загрязнения на оболочке: {percent :.2f}% { 'критично' if percent>10 else '' }")



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



