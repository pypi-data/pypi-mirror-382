from qtpy.QtCore import QObject
from PyQt5.QtCore import pyqtSignal, pyqtSlot

# For the inference widget:

class QtUNetInference(QObject):

    update   = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.model = model

    def callback(self, im_name):
        self.update.emit(im_name)

    def run(self):
        try:
            self.model.run_inference(self.callback)
            self.finished.emit()
        except Exception as e:
            self.finished.emit()

class QtUNetRefreshMasks(QObject):

    update   = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.model = model

    def callback(self, im_name):
        self.update.emit(im_name)

    def run(self):
        try:
            self.model.refresh_masks(self.callback)
            self.finished.emit()
        except Exception as e:
            self.finished.emit()


# For the training widget:

class QtUNetTraining(QObject):

    update   = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, trainer):
        super().__init__()
        self.trainer = trainer

    def callback(self, epoch_idx):
        self.update.emit(epoch_idx)

    def run(self):
        try:
            self.trainer.train(self.callback)
            self.finished.emit()
        except Exception as e:
            self.finished.emit()